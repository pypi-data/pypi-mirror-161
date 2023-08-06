"""Contains classes used for logging ML models to the tracking server

The wrapper classes contained in this section allow for logging model artifacts from
a number of supported libraries. The `Wrapper.log_model` implementation in each library-specific
wrapper class takes care of serializing a trained ML model to disk, constructing an appropriate directory
structure, packaging all artifacts with additional necessary metadata and uploading it to S3 as a deployable
payload
"""

import os
import requests
from urllib3 import Retry
from .inference import *
import tarfile
import shutil
import uuid
import time
import joblib

class Wrapper(object):
    """Base class for Cortex library wrappers
    
    This class is meant to be inherited and is NOT meant to be instantiated explicitly

    Args:
        client (cortex.cortex.CortexClient): An instance of the `cortex.cortex.CortexClient`
        ml_library (str): Name of the ML library the wrapper is meant to be used for
    """
    def __init__(self, client, ml_library):
        self.client = client
        """An instance of `cortex.cortex.CortexClient`"""
        self.library = ml_library
        """ML Library name"""

    def log_model(
        self, 
        model, 
        scratch_directory="model",
        signature=None, 
        run_name=None, 
        run_description=None, 
        cortex_experiment_id=None, 
        dataset_version_id=None,
        dataset_input_columns=None,
        dataset_output_columns=None,
        **kwargs):
        """Logs a trained ML model to the tracking server

        Args:
            model (object): A trained ML model from a specific library
            scratch_directory (str): Temporary directory for saving the serialized model and other assets before upload
            signature (cortex.schemas.CortexSignature, optional): An instance of `cortex.schemas.CortexSignature` that describes the model's I/O schema
            run_name (str, optional): The name for this Run
            run_description (str, optional): The description for this Run
            cortex_experiment_id (str, optional): ID of the Cortex Experiment associated with this Run
            dataset_version_id (str, optional): ID of the Cortex Dataset this model was trained on
            dataset_input_columns (list of str, optional): List of dataset column names used as inputs for training
            dataset_output_columns (list of str, optional): List of dataset column names used as outputs for training

        Typical usage example:

            >>> client = CortexClient("MY-TOKEN-HERE")
            >>> run = client.pytorch.log_model(
                model,
                run_name = "Parameters, Metrics, Signature, Dataset",
                run_description = "Test run with Parameters, Metrics, Signature and Dataset",
                cortex_experiment_id = exp["_id"],
                signature = signature,
                dataset_version_id=cursor.dataset_version_id(),
                dataset_input_columns=list(X.columns),
                dataset_output_columns=list(y.columns)
            )
        """



        # Create artifact directory
        temp_folder = os.path.join(scratch_directory, str(uuid.uuid4()))
        os.makedirs(temp_folder)

        # Log model to Cortex API
        library_version = self.get_library_version()

        # Create run
        run = self.client.create_run(
            name=run_name, 
            description=run_description, 
            experimentId=cortex_experiment_id, 
            signature=signature, 
            libraryName=self.library,
            libraryVersion=library_version,
            datasetVersionId=dataset_version_id,
            dataset_input_columns=dataset_input_columns,
            dataset_output_columns=dataset_output_columns)


        # Create tarball
        tarball_path = self.save_tarball(model, temp_folder, run["_id"])

        # Upload tarball
        key = "models/{0}/{1}.tar.gz".format(self._make_S3_key_compatible(self.library), run["_id"])
        self._upload({key: tarball_path})

        # Update logged run with the S3 key
        self.client.update_payload_key(run["_id"], key)

        # Clear client metadata
        self.client.purge_metadata()

        # Clean up
        shutil.rmtree(temp_folder)

        return self.client.get_run_by_id(run["_id"])
    

    def _upload(self, keys_dict):
        #print("headers", headers)

        keys_response = self.client.get_artifact_upload_urls(keys_dict.keys())
        uri_dict = {}
        
        for obj in keys_response:
            s3key = obj["key"]
            url = obj["url"]
            uri_dict[s3key] = url

        for key in keys_dict:
            filepath = keys_dict[key]
            url = uri_dict[key]

            if os.stat(filepath).st_size == 0:
                put_request = requests.put(url, "")
                #print("Empty put")
            else:
                with open(filepath, "rb") as file:
                    put_request = requests.put(url, file)
                #print("Put something there")
            #print()
            put_request.raise_for_status()
        
        #print("UPLOADED!")

    def _make_S3_key_compatible(self, string):
        nStr = string.lower()
        illegal = [".", " ", "@", "#", "%", "^", "*", ":", ";", "\\", "/"]
        for char in illegal:
            if char in nStr:
                nStr = nStr.replace(char, "-")

        return nStr


class PyTorch_Wrapper(Wrapper):
    """A wrapper class for logging PyTorch ML models

    This class is NOT meant to be instantiated directly. An instance of the `PyTorch_Wrapper` is created with each new
    `cortex.cortex.CortexClient` and is available under `cortex.cortex.CortexClient.pytorch`

    Typical usage example:

        >>> client = CortexClient("MY-TOKEN-HERE")
        >>> run = client.pytorch.log_model(
                model,
                run_name = "My PyTorch run",
                run_description = "Just testing some stuff out",
                cortex_experiment_id = exp["_id"],
                signature = signature
            )
    """
    def __init__(self, client):
        super(PyTorch_Wrapper, self).__init__(client, "PyTorch")

    def get_library_version(self):
        """Returns the version of the ML library
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import torch
        return torch.__version__

    def save_tarball(self, model, payload_dir, run_id):
        """Saves all assets as a `.tar` archive
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import torch

        run_dir = os.path.join(payload_dir, run_id)
        os.mkdir(run_dir)

        code_dir = os.path.join(run_dir, "code")
        os.mkdir(code_dir)

        scripted_model = torch.jit.script(model)
        scripted_model.save(os.path.join(run_dir,'model.pt'))

        inference_path = os.path.join(code_dir, "inference.py")

        with open(inference_path, "w") as f:
            f.write(PYTORCH_INFERENCE)

        tar_name = str(run_id) + ".tar.gz"
        tar_path = os.path.join(payload_dir, tar_name)

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(run_dir, arcname=os.path.sep)

        return tar_path


class Sklearn_Wrapper(Wrapper):
    """A wrapper class for logging Scikit-Learn ML models

    This class is NOT meant to be instantiated directly. An instance of the `Sklearn_Wrapper` is created with each new
    `cortex.cortex.CortexClient` and is available under `cortex.cortex.CortexClient.sklearn`

    Typical usage example:

        >>> client = CortexClient("MY-TOKEN-HERE")
        >>> run = client.sklearn.log_model(
                model,
                run_name = "My Scikit-Learn run",
                run_description = "Just testing some stuff out",
                cortex_experiment_id = exp["_id"],
                signature = signature
            )
    """
    def __init__(self, client):
        super(Sklearn_Wrapper, self).__init__(client, "Scikit-Learn")

    def get_library_version(self):
        """Returns the version of the ML library
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import sklearn
        return sklearn.__version__

    def save_tarball(self, model, payload_dir, run_id):
        """Saves all assets as a `.tar` archive
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import sklearn
        run_dir = os.path.join(payload_dir, run_id)
        os.mkdir(run_dir)
        
        # Save the model
        joblib.dump(model, os.path.join(run_dir, "model.joblib"))

        inference_path = os.path.join(run_dir, "inference.py")

        with open(inference_path, "w") as f:
            f.write(SCIKIT_INFERENCE)

        tar_name = str(run_id) + ".tar.gz"
        tar_path = os.path.join(payload_dir, tar_name)

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(run_dir, arcname=os.path.sep)

        return tar_path

class TensorFlow_Wrapper(Wrapper):
    """A wrapper class for logging Tensorflow/Keras ML models

    This class is NOT meant to be instantiated directly. An instance of the `TensorFlow_Wrapper` is created with each new
    `cortex.cortex.CortexClient` and is available under `cortex.cortex.CortexClient.tensorflow`

    Typical usage example:

        >>> client = CortexClient("MY-TOKEN-HERE")
        >>> run = client.tensorflow.log_model(
                model,
                run_name = "My Tensorflow run",
                run_description = "Just testing some stuff out",
                cortex_experiment_id = exp["_id"],
                signature = signature
            )
    """
    def __init__(self, client):
        super(TensorFlow_Wrapper, self).__init__(client, "TensorFlow")

    def get_library_version(self):
        """Returns the version of the ML library
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import tensorflow
        return tensorflow.__version__

    def save_tarball(self, model, payload_dir, run_id):
        """Saves all assets as a `.tar` archive
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import tensorflow
        run_dir = os.path.join(payload_dir, run_id)
        os.mkdir(run_dir)

        major_version = tensorflow.__version__.split(".")[0]
        model.save(os.path.join(run_dir, major_version))

        tar_name = str(run_id) + ".tar.gz"
        tar_path = os.path.join(payload_dir, tar_name)

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(run_dir, arcname=os.path.sep)

        return tar_path


class XGBoost_Wrapper(Wrapper):
    """A wrapper class for logging XGBoost ML models

    This class is NOT meant to be instantiated directly. An instance of the `XGBoost_Wrapper` is created with each new
    `cortex.cortex.CortexClient` and is available under `cortex.cortex.CortexClient.xgboost`

    Typical usage example:

        >>> client = CortexClient("MY-TOKEN-HERE")
        >>> run = client.xgboost.log_model(
                model,
                run_name = "My XGBoost run",
                run_description = "Just testing some stuff out",
                cortex_experiment_id = exp["_id"],
                signature = signature
            )
    """
    def __init__(self, client):
        super(XGBoost_Wrapper, self).__init__(client, "XGBoost")

    def get_library_version(self):
        """Returns the version of the ML library
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import xgboost
        return xgboost.__version__

    def save_tarball(self, model, payload_dir, run_id):
        """Saves all assets as a `.tar` archive
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the parent class
        """
        import xgboost
        run_dir = os.path.join(payload_dir, run_id)
        os.mkdir(run_dir)

        model.save_model(os.path.join(run_dir, "xgboost-model"))

        tar_name = str(run_id) + ".tar.gz"
        tar_path = os.path.join(payload_dir, tar_name)

        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(run_dir, arcname=os.path.sep)

        return tar_path
