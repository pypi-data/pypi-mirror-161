"""Main module of Cortex's Python SDK

This module contains the `CortexClient` class, which is the primary way of interacting with
the Cortex web API from Python. Pretty much any code involving Cortex will start with
instantiating a new client
"""
from __future__ import division
import os
from platform import python_version
import requests
import json
from pprint import pprint
from datetime import datetime

import sys

import ntpath
import math
import csv
import shutil


from .routes_controller import RoutesController
from .cortex_cursor import CortexCursor
from .wrappers import *
from .metadata import LogEntry, Metadata

from requests.api import request
import time

import platform
import inspect


class CortexClient():
    """The main client class for the Cortex web API

    This class allows the user to perform the majority of the functions available 
    through the web app interface. It also provides a way to log ML models and 
    metadata to the tracking server.

    Args:
        cortex_token (str): An auth token that can be obtained from the `Account` section
            of the Cortex web app under `API Access`
        endpoint (str): An override that lets you point the `CortexClient` to a version of the Cortex
            web app that is different from production (e.g. staging). For debugging purposes only.
        local_node (bool): If `True`, points the `CortexClient` to a local version of the Cortex server.
            The same result can be achieved by passing `http://localhost:1337` as an `endpoint` argument,
            so this is only for convenience. For debugging purposes only.

    Typical usage example:

        >>> client = CortexClient("MY_CORTEX_TOKEN_HERE")   
        >>> experiments = client.get_all_experiments()
    """
    def __init__(self,  
        cortex_token,
        endpoint="https://core-cortex.herokuapp.com", 
        local_node=False
        ):

        # Routes
        self.__auth_headers = { "Content-Type": "application/json" }
        if local_node:
            endpoint = "http://localhost:1337"

        # Defend against URLs that end with /
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]

        self.routes_controller = RoutesController(endpoint, self.__auth_headers)

        # Auth
        self.__authenticate(cortex_token)
        
        # Wrappers
        self.sklearn = Sklearn_Wrapper(self)
        """An instance of the `cortex.wrappers.Sklearn_Wrapper` object for logging Scikit-Learn models"""
        self.pytorch = PyTorch_Wrapper(self)
        """An instance of the `cortex.wrappers.PyTorch_Wrapper` object for loggig Pytorch models"""
        self.xgboost = XGBoost_Wrapper(self)
        """An instance of the `cortex.wrappers.XGBoost_Wrapper` object for logging XGBoost models"""
        self.tensorflow = TensorFlow_Wrapper(self)
        """An instance of the `cortex.wrappers.TensorFlow_Wrapper` object for logging Tensorflow-Keras models"""

        #Logging
        self.metadata = Metadata()

    def __authenticate(self, cortex_token):
        self.__token = cortex_token

        if self.__token is None:
            raise Exception("Token cannot be null")

        result = self.__api_post(
            self.routes_controller.validate_token(), 
            {
                "token" : cortex_token
            })

        if not result["is_valid"]:
            raise Exception("Invalid Cortex token")

        self.__auth_headers["Authorization"] = "Basic {0}".format(self.__token)
        return True

    ## MISC
    def purge_metadata(self):
        """Resets the `Metadata` collection

        Resets the `CortexClient` metadata collection by creating a new instance of the `Metadata` class.
        Useful for situations where loging happens several times within the same script, or in case of 
        a Jupyter notebook

        Typical usage example:

            >>> client.purge_metadata()
            >>> 
        """
        self.metadata = Metadata()

    ## LOGGING
    def log_param(self, key, value, epoch=0):
        """Adds a hyperparameter to the `Metadata` collection

        Lets you log model hyperparameters to the remote tracking server. The parameters are first added
        to the local `Metadata` collection of the `CortexClient`. Then, once `log_model(...)` is called, 
        the hyperparameters are sent to the tracking server all at once

        Args:
            key (str): Hyperparameter name
            value: Hyperparameter value of type `str`, `int`, `float` or `bool`
            epoch (int, optional): Training epoch (in case if the hyperparameters are captured over multiple training cycles)

        Typical usage example:

            >>> # Logging once per session
            >>> client.log_param("learning_rate", 0.001)
            >>> client.log_param("optimizer", "adam")
            >>> client.log_param("dropout", 0.0)
            >>> client.log_param("reduction", "sum")
            >>> client.log_param("no_epoch", 500)
            >>> client.log_param("patience", 20)
            >>>
            >>> # Logging once per epoch
            >>> num_epochs = 500
            >>> lr = 0.05
            >>> for epoch in range(num_epochs):
                   client.log_param("learning_rate", lr, epoch)
                   lr -= 0.001

        """
        self.metadata.log_param(LogEntry(key, value, epoch))

    def log_metric(self, key, value, epoch=0):
        """Adds an evaluation metric to the `Metadata` collection

        Lets you log model evaluation metrics to the remote tracking server. The metrics are first added
        to the local `Metadata` collection of the `CortexClient`. Then, once `log_model(...)` is called,
        the metrics are sent to the tracking server all at once.

        Args:
            key (str): Evaluation metric name
            value: Evaluation metric value of type `str`, `int`, `float` or `bool`
            epoch (int, optional): Training epoch (in case if the hyperparameters are captured over multiple training cycles)

        Typical usage example:
            
            >>> # Logging once per session
            >>> client.log_metric("train loss", train_loss)
            >>> client.log_metric("value loss", val_loss)
            >>> client.log_metric("mse", mean_sq_error)
            >>> 
            >>> # Logging once per epoch
            >>> num_epochs = 500
            >>> for epoch in range(num_epochs):
                    client.log_metric("train loss", train_loss, epoch)
                    client.log_metric("value loss", val_loss, epoch)
                    client.log_metric("mse", mean_sq_error, epoch)
            
        """
        self.metadata.log_metric(LogEntry(key, value, epoch))

    ## HTTP
    def __post(self, url, payload):
        response = requests.post(url, data=json.dumps(payload), headers=self.routes_controller.auth_headers)
        if str(response.status_code).startswith("2"):
            return response
        else:
            print("HTTP code:", response.status_code)
            print("Reason:", response.reason)
            print("Text:", response.text)
            raise Exception("Server returned an error")

    def __get(self, url):
        response = requests.get(url, headers=self.routes_controller.auth_headers)
        if str(response.status_code).startswith("2"):
            return response
        else:
            print("HTTP code:", response.status_code)
            print("Reason:", response.reason)
            print("Text:", response.text)
            raise Exception("Server returned an error")

    def __delete(self, url):
        response = requests.delete(url, headers=self.routes_controller.auth_headers)
        if str(response.status_code).startswith("2"):
            return response
        else:
            print("HTTP code:", response.status_code)
            print("Reason:", response.reason)
            print("Text:", response.text)
            raise Exception("Server returned an error")

    def __api_post(self, url, payload):
        response = self.__post(url, payload)
        return self.__unpack_response(response.text)


    def __api_get(self, url):
        response = self.__get(url)
        return self.__unpack_response(response.text)

    def __api_delete(self, url):
        response = self.__delete(url)
        print(response)
        return self.__unpack_response(response.text)

    def __unpack_response(self, response:str):
        data = json.loads(response)
        if (data["error"] != None):
            raise Exception(data["message"])
        else:
            return data["data"]

    # CREATE
    def create_experiment(self, name, description=None):
        """Creates a new Cortex Experiment on the web app

        Creates a new Experiment on the web app. Experiments are essentially projects that contain Runs.
        Multiple Experiments with the same name are allowed, so it's a good idea to check whether or
        not an experiment with this name already exists before logging a new one in order to avoid duplicates

        Args:
            name (str): Experiment name (duplicate names are allowed)
            description (str): Experiment description

        Returns:
            dict: A dictionary representing a newly created Experiment

        Typical usage example:
            
            >>> experiment_name = "Pytorch test"
            >>> experiment_description = "Pytorch test runs"
            >>> exp = client.get_experiment_by_name(experiment_name)
            >>> if exp is None:
                   exp = client.create_experiment(
                     experiment_name, 
                     experiment_description)
            >>> print(exp)
            {"APIToken": "",
            "__v": 0,
            "_id": "62ba16a11259af1a6b1fd9a9",
            "created": {"date": "2022-06-27T20:44:17.357Z",
                        "user": {"_id": "628c7f47712eb35642f9c4ab",
                                "sso": {"email": "tanderson@gmail.com",
                                        "profile": {"name": "Thomas Anderson"}}}},
            "description": "Pytorch test runs",
            "isPublic": False,
            "models": [],
            "modified": {"date": "2022-06-27T20:44:17.357Z",
                        "user": "628c7f47712eb35642f9c4ab"},
            "name": "Pytorch test",
            "rootFolder": {"__v": 0,
                            "_id": "62fa18a13249af1a7b1fd9fb",
                            "name": "Project Root Folder",
                            "path": "/Project Root Folder",
                            "project": "62ba16a11259af1a6b1fd9a9"},
            "runs": [],
            "users": [{"_id": "62ba17f11759af1a8b1ed9aa",
                        "permissions": {"delete": True, "edit": True, "view": True},
                        "user": {"_id": "628c7f47712eb35642f9c4ab",
                                "sso": {"email": "tanderson@gmail.com",
                                        "profile": {"name": "Thomas Anderson"}}}}]}
                    """
        payload ={
            "name": name,
            "description": description
        }
        url = self.routes_controller.new_experiment_url()
        return self.__api_post(url, payload)


    def create_model(self, name, description=None, experiment_id=None):
        """Creates a new Model interface on the web app

        Creates a new Model on the web app. A Cortex Model is an abstract interface that allows
        external applications run inference on a deployed Cortex Run. Not to be confused with a
        local ML model, which turns into a Run when logged. Essentially, a Model is a publicly
        available Run

        Args:
            name (str): Model name (duplicate names are allowed)
            description (str, optional): Model description
            experiment_id (str, optional): ID of an experiment to assign this model to. If `None`, a
            new experiment with a default name will be created

        Returns:
            dict: A dictionary representing a newly created Model

        Typical usage example:

            >>> name = "Column Designer"
            >>> description = "ML model for designing columns"
            >>> exp = vlient.get_experiment_by_name(experiment_name)
            >>> model = client.create_model(name, description, exp["_id"])
            >>> print(model)
            {"_id":"612d29ade3d3e600179c038c",  
            "isExposed":false,  
            "user":"5feb442f16ae4900166fbb83",  
            "name":"Column Designer",  
            "description":"ML model for designing columns",  
            "run":None,  
            "experiment":"612d2640e3d3e600179c0360",  
            "status":"",  
            "__v": 0}
        """
        eid = experiment_id
        if eid is None:
            now = datetime.now()
            timestamp = now.strftime("%m/%d/%Y-%H:%M:%S")
            eid = self.create_experiment("Untitled {0}".format(timestamp))["_id"]


        payload={
            "name": name,
            "description": description,
            "experimentId": eid
        }
        url = self.routes_controller.new_model_url()
        return self.__api_post(url, payload)


    def create_run(
        self,  
        name=None, 
        description=None, 
        experimentId=None, 
        signature=None, 
        libraryName="N/A", 
        libraryVersion="N/A",
        datasetVersionId=None,
        dataset_input_columns=None,
        dataset_output_columns=None):
        """Creates a new Cortex Run (not meant to be called explicitly)

        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the `Wrapper` modules
        """

        eid = experimentId
        rn = name
        if experimentId is None:
            now = datetime.now()
            timestamp = now.strftime("%m/%d/%Y-%H:%M:%S")
            eid = self.create_experiment("Untitled {0}".format(timestamp))["_id"]

        if rn is None:
            if libraryName != "N/A":
                rn = str("Unnamed {0} Run".format(libraryName))
            else:
                rn = str("Unnamed Run")

        source_file_name = None
        python_version = None
        
        try:
            import ipynbname
            source_file_name = ipynbname.name() + ".ipynb"
            
        except:
            try:
                frame = inspect.stack()[-1]
                module = inspect.getmodule(frame[0])
                source_file_name = os.path.basename(module.__file__)
            except:
                pass

        try:
            python_version = platform.python_version()
        except:
            pass

        payload={
            "name": rn,
            "description": description,
            "timeLogged": int(time.time()),
            "experimentId": eid,
            "library": libraryName,
            "libraryVersion": libraryVersion,
            "datasetVersionId": datasetVersionId,
            "datasetInputColumns": dataset_input_columns,
            "datasetOutputColumns": dataset_output_columns,
            "metadata": self.metadata.toDict(),
            "sourceFilename": source_file_name,
            "pythonVersion": python_version
        }

        if signature is not None:
            payload["signature"] = signature.toDict()

        url = self.routes_controller.new_run_url()
        return self.__api_post(url, payload)

    def __create_multipart_upload(self, key):
        payload = {
            "key" : key
        }

        url = self.routes_controller.create_multipart_upload()
        return self.__api_post(url, payload)

    def __complete_multipart_upload(self, key, multipart_upload, upload_id):
        payload = {
            "key" : key,
            "multipartUpload" : multipart_upload,
            "uploadId" : upload_id
        }

        url = self.routes_controller.complete_multipart_upload()
        return self.__api_post(url, payload)

    def create_dataset(self, name, description, is_public=False):
        """Creates a new empty dataset on the web app

        Creates an empty `Dataset` object on the web app. Adding the actual data involves adding a new
        version via the `CortexClient.upload_dataset_version` method

        Args:
            name (str): Dataset name (duplicate names are allowed)
            description (str): Dataset description
            is_public (bool): A flag indicating whether or not the newly created dataset should be public
        
        Returns:
            dict: A dictionary representing a newly created Dataset

        Typical usage example:

            >>> name = "Timber Dataset"
            >>> description = "Structural dataset for timber design"
            >>> dataset = client.create_dataset(name, description, True)
            >>> print(dataset)
            {"isPublic": True, 
            "isArchived": False, 
            "_id": "62d5d3043efd7500161832ce", 
            "name": "Timber Dataset", 
            "description": "Structural dataset for timber design", 
            "created": {"date": "2022-07-18T21:39:16.706Z", "user": "629a7f17742ec35642e9c4bb"}, 
            "users": [{"permissions": {"view": True, "delete": True, "edit": True}, 
            "_id": "62d5d3043efd7500161832cf", 
            "user": "629a7f17742ec35642e9c4bb"}], 
            "__v": 0}
        """
        payload = {
            "name" : name,
            "description": description,
            "isPublic": is_public
        }

        url = self.routes_controller.create_dataset()
        return self.__api_post(url, payload)

    def __add_dataset_version(self, version_name, message, filename, dataset_id, num_rows, headers, make_current=True):
        payload = {
            "name": version_name,
            "message": message,
            "filename": filename,
            "totalRows": num_rows,
            "headers": headers,
            "makeCurrent": make_current
        }
        
        url = self.routes_controller.create_dataset_version(dataset_id)
        return self.__api_post(url, payload)



    # GET
    def get_all_experiments(self):
        """Fetches all Experiments that belong to the user
        
        Returns:
            list of dict: A list of dictionaries each representing an experiment
            
        Typical usage example:
        
            >>> experiments = client.get_all_experiments()
            >>> print(len(experiments))
            5
        """
        return self.__api_get(self.routes_controller.get_all_projects_url())

    def get_experiment_by_id(self, id):
        """Fetches an Experiment by its ID

        Args:
            id (str): ID of the Experiment to fetch
        
        Returns:
            dict: A dictionary representing an Experiment
            
        Typical usage example:
        
            >>> exp_id = "629a7f17742ec35642e9c4bb"
            >>> my_experiment = client.get_experiment_by_id(exp_id)
            >>> print(my_experiment["name"])
            Tensorflow Test"""
        return self.__api_get(self.routes_controller.get_project_info_url(id))

    def get_experiments_by_name(self, name, match_case=False):
        """Fetches Experiments whose name matches the search string

        This method returns all experiments whose name partially or fully matches
        the search string

        Args:
            name (str): A search string for the Experiment name
            match_case (bool, optional): A toggle for whether or not the search should be case sensitive

        Returns:
            list of dict: A list of dictionaries representing found experiments

        Typical usage example:

            >>> name = "column"
            >>> experiments = client.get_experiments_by_name(name)
            >>> [e["name"] for e in experiments]
            ["Asterisk Columns", "Column designer", "Pytorch Columns Test"]
        """
        payload = {"name": name, "match_case": match_case}
        url = self.routes_controller.get_projects_by_name_url()
        return self.__api_post(url, payload)

    def get_experiment_by_name(self, name, match_case=False):
        """Fetches the first Experiment whose name matches the search string

        This method returns the first experiment whose name partially or fully
        mtches the search string

        Args:
            name (str): A search string for the Experiment name
            match_case (bool, optional): A toggle for whether or not the search should be case sensitive

        Returns:
            dict: A dictionary representing the found experiment. If no experiments were found, `None` is returned

        Typical usage example:

            >>> name = "My XGBoost Experiment"
            >>> description = "Just testing some stuff out"
            >>> exp = client.get_experiment_by_name(name)
            >>> if exp is None:
                   exp = client.create_experiment(name, description)
            >>> print(exp["_id"])
            629a7f17742ec35642e9c4bb
        """
        matching = self.get_experiments_by_name(name, match_case)
        if len(matching) > 0:
            return matching[0]
        else:
            return None

    def get_run_by_id(self, id):
        """Fetches a Run by its ID

        Args:
            id (str): Run ID

        Returns:
            dict: A dictionary representing the Run

        Typical usage examples:

            >>> run = client.get_run_by_id("629a7f17742ec35642e9c4bb")
            >>> print(run["name"])
            Pytorch Run 1
        """
        return self.__api_get(self.routes_controller.get_run_info_url(id))

    def get_model_by_id(self, id):
        """Fetches a Model by its ID

        Args:
            id (str): Model ID

        Returns:
            dict: A dictionary representing the Model

        Typical usage example:
        
            >>> model = client.get_model_by_id("629a7f17742ec35642e9c4bb")
            >>> print(model["name"])
            "Timber Model"
        """
        url = self.routes_controller.get_model_info_url(id)
        return self.__api_get(url)

    def __get_s3_bucket(self):
        url = self.routes_controller.get_s3_bucket_url()
        return self.__api_get(url)["bucket"]

    def __get_s3_signed_urls(self, keys_list):
        payload = {
            "keys": []
        }

        for k in keys_list:
            payload["keys"].append({"key" : k})

        # pprint(payload)
        url = self.routes_controller.get_s3_signed_urls()
        return self.__api_post(url, payload)

    def get_artifact_upload_urls(self, keys_list):
        """Converts S3 keys to signed URLs for asset upload

        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the `Wrapper` modules
        """
        payload = {
            "keys": []
        }

        for k in keys_list:
            payload["keys"].append({"key" : k})

        # r = requests.post(self.routes_controller.get_s3_signed_urls(), data=json.dumps(payload), headers=self.routes_controller.auth_headers)
        url = self.routes_controller.get_s3_signed_urls()
        return self.__api_post(url, payload)

    def __get_s3_signed_url_for_multipart_upload(self, key, upload_id, part_number):
        payload = {
            "key" : key,
            "upload_id" : upload_id,
            "part_number" : part_number
        }

        url = self.routes_controller.get_s3_signed_url_for_multipart_upload()
        return self.__api_post(url, payload)

    def get_artifact_uri(self, flavor, run_id, instance_number="001"):
        """Formats an S3 key for artifact upload

        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the `Wrapper` modules
        """
        bucket = self.__get_s3_bucket()
        dest_path = "endpoints/{0}/{1}/artifacts/{2}".format(flavor, instance_number, run_id)
        return bucket, dest_path

    def get_datasets_by_name(self, name):
        """Fetches all Datasets whose name matches the search string

        This method returns all datasets whose name partially or fully matches
        the search string

        Args:
            name (str): A search string for the Dataset name

        Returns:
            list of dict: A list of dictionaries representing found datasets

        Typical usage example:

            >>> datasets = client.get_datasets_by_name("timber")
            >>> [d["name"] for d in datasets]
            ["Timber Dataset", "Timber Design", "Laminated timber"]
        """
        payload = {
            "name" : name
        }
        url = self.routes_controller.get_multiple_datasets_by_name_url()
        return self.__api_post(url, payload)

    def get_dataset_by_name(self, name):
        """Fetches the first Dataset whose name matches the search string

        This method returns the first dataset whose name partially or fully
        mtches the search string

        Args:
            name (str): A search string for the dataset name

        Returns:
            dict: A dictionary representing the found Dataset. If no datasets were found, 'None' is returned

        Typical usage example:
            
            >>> dataset = client.get_dataset_by_name("timber")
            >>> print(dataset["name"])
            Timber Design
        """
        payload = {
            "name" : name
        }
        url = self.routes_controller.get_one_dataset_by_name_url()
        return self.__api_post(url, payload)

    def get_dataset_by_id(self, id):
        """Fetches a Dataset by its ID

        Args:
            id (str): ID of the Dataset

        Returns:
            dict: A dictionary representation of the dataset

        Typical usage example:
            
            >>> dataset = client.get_dataset_by_id("629a7f17742ec35642e9c4bb")
            >>> print(dataset["name"])
            Iris Dataset
        """
        url = self.routes_controller.get_dataset_by_id_url(id)
        return self.__api_get(url)

    def get_my_datasets(self):
        """Fetches all datasets that belong to the user

        Returns:
            list of dict: A list of dictionaries representing Cortex Datasets

        Typical usage example:

            >>> datasets = client.get_my_datasets()
            >>> print(len(datasets))
            34
        """
        url = self.routes_controller.get_my_datasets_url()
        return self.__api_get(url)

    def list_datasets(self):
        """Prints a table with all datasets that belong to the user

        Typical usage example:
            
            >>> client.list_datasets()
            Datasets:
            Steel Column Dataset       [62d6ce4dd0fb6200167f78fa]
            Rocket Telemetry           [62d5d3043efd7500161832ce]
            Concrete Slab              [62bd73700cb1eb5a281e872f]
            Shear Tab Connections      [62a90894ee68522bd42808a0]
            Monthly Car Sales          [62a90170ee68522bd4280885]
            Iris                       [62a8f780ee68522bd4280869]
            Timber                     [62a8b7e7fbbf6c6afd311eb3]
        """
        print("Datasets:")
        datasets = self.get_my_datasets()
        longest_name = 0
        for d in datasets:
            if len(d["name"]) > longest_name:
                longest_name = len(d["name"])
        
        for d in self.get_my_datasets():
            name = d["name"]
            padding = " " * (longest_name - len(name) + 4)
            print(name, padding, "[" + d["_id"] + "]")

    def get_dataset_versions(self, dataset_id):
        """Fetches all versions associated with a dataset

        Args:
            dataset_id (str): The ID of the dataset to fetch versions from

        Returns:
            list of dict: A list of dictionaries representing dataset versions

        Typical usage example:

            >>> dataset = client.get_dataset_by_name("iris")
            >>> versions = client.get_dataset_versions(dataset["_id"])
            >>> print(len(versions))
            3
        """
        url = self.routes_controller.list_dataset_versions_url(dataset_id)
        return self.__api_get(url)

    def list_dataset_versions(self, dataset_id):
        """Prints a table with all versions contained in a dataset

        Current version of the dataset is marked with the [+] sign

        Args:
            dataset_id (str): The ID of the dataset to list versions from

        Typical usage example:

            >>> dataset = client.get_dataset_by_name("iris")
            >>> client.list_dataset_versions(dataset["_id"])
            Dataset [62bd73700cb1eb5a281e872f] versions:
            [ ]  v1      [62bd73740cb1eb5a281e8736] 	 2022-06-30T09:57:08.456Z
            [ ]  v2      [62a8b7e7fbbf6c6afd311eb3]      2022-07-12T05:11:17.243Z
            [+]  v3      [62a8f780ee68522bd4280869]      2022-07-15T01:45:21.437Z
        """
        versions = self.get_dataset_versions(dataset_id)
        dataset = self.get_dataset_by_id(dataset_id)
        current_id = dataset["currentVersion"]["_id"]

        longest_version_name = 0
        for v in versions:
            if len(v["name"]) > longest_version_name:
                longest_version_name = len(v["name"])
        print("Dataset [{0}] versions:".format(dataset_id))
        for v in versions:
            check_box = "[ ] "
            name = v["name"]
            padding = " " * (longest_version_name - len(name) + 4)
            if v["_id"] == current_id:
                check_box = "[+] "
            print(check_box, name, padding, "[" + v["_id"] + "]", "\t", v["uploaded"])

    def __list_to_csv_line(self, array):
        line = ""
        for e in array:
            if "," in e:
                line += "\"{0}\",".format(e)
            else:
                line += "{0},".format(e)

        line = line[:-1]
        line += "\n"
        return line


    def download_dataset(self, dataset_id, filepath=None, scratch_directory="scratch"):
        """Downloads a dataset locally and saves it to a file

        Args:
            dataset_id (str): ID of the dataset to download
            filepath (str, optional): Filepath to save the dataset
            scratch_directory (str): Temporary directory for downloading datasets in sections before stitching them back into a single file

        Returns:
            str: File path to saved dataset

        Typical usage example:

            >>> dataset = client.get_dataset_by_name("iris")
            >>> path = client.downlod_dataset(dataset["_id"])
            >>> print(path)
            iris.csv
        """
        if not os.path.isdir(scratch_directory):
            os.makedirs(scratch_directory)

        dataset = self.get_dataset_by_id(dataset_id)
        if filepath is None:
            file_name = dataset["currentVersion"]["filename"]
        else:
            file_name = filepath

        print("Downloading", dataset["name"], "to", file_name)
        keys = dataset["currentVersion"]["keys"]
        
        first_chunk = True
        total = len(keys)
        index = 1
        with open(file_name, "w") as f:
            self.__print_progress_bar(total, 0)
            for k in keys:
                url = self.__get_download_key(k)
                result = requests.get(url)
              
                table = result.text.split("\n")

                header = table[0]
                if first_chunk:
                    f.write(header + "\n")
                    first_chunk = False

                for l in table[1:]:
                    if l != "":
                        f.write(l + "\n")

                self.__print_progress_bar(total, index)
                index += 1
        print("Download complete!")

        return file_name

    def get_dataset_cursor(self, dataset_id):
        """Returns an instance of `cortex.cortex_cursor.CortexCursor` for traversing a dataset

        Returns a `cortex.cortex_cursor.CortexCursor` object that allows you to load the
        dataset in small consequitive batches. This is useful for batch training
        on a giant dataset, where downloading it locally is not convenient or possible

        Args:
            dataset_id (str): ID of the dataset to instantiate a Cursor for

        Returns:
            `cortex.cortex_cursor.CortexCursor`: A cursor object for traversing the dataset

        Typical usage example:

            >>> dataset = client.get_dataset_by_name("timber")
            >>> cursor = client.get_dataset_cursor(dataset["_id"])
            >>> done = False
            >>> while not done:
                    batch, done = cursor.fetch_next(num_rows=512)
                    // do stuff with the batch
        """
        dataset = self.get_dataset_by_id(dataset_id)
        cursor = CortexCursor(self.routes_controller.server, dataset, self.routes_controller.auth_headers)
        return cursor
        
    
    # MODIFY
    
    def assign_run_to_model(self, modelId, runId):
        """Assigns a logged Run to an abstract Model interface

        This method is used to assign a `Run` to a Cortex `Model`. Models provide an interface that make
        a deployed Run accessible from outside of Cortex. Not to be confused with an `ML model` that,
        when logged, turns into a Cortex Run. A good way to think about this is that Runs are always private,
        whereas Models can be public and can therefore expose an otherwise private Run to the outside world

        Args:
            modelId (str): ID of an existing model
            runId (str): ID of a deployed run

        Returns:
            dict: A dictionary representing an updated Model object

        Typical usage example:
            
            >>> model = client.assign_run_to_model(myModel["_id"], myRun["_id"])
            >>> print(model)
            {"_id":"612d29ade3d3e600179c038c",  
            "isExposed":true,  
            "user":"5feb442f16ae4900166fbb83",  
            "name":"Beam Sizer",  
            "description":"Beam Sizer Classification Model",  
            "run":"612d2645e3d3e600179c0363",  
            "experiment":"612d2640e3d3e600179c0360",  
            "status":"InService",  
            "__v": 0}
        """
        payload = {
            "runId": runId
        }
        url = self.routes_controller.assign_run_url(modelId)
        # print(url)
        return self.__api_post(url, payload)


    def update_payload_key(self, runId, key):
        """Updates the Run object in the database with the S3 key of uploaded assets

        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible from the `Wrapper` modules
        """
        payload = {
            "s3_key": key
        }
        url = self.routes_controller.update_payload_key(runId)
        return self.__api_post(url, payload)

    # UPLOAD
    def __format_bytes(self, size):
        size_string = "{0} Bytes".format(size)
        
        if (size >= pow(1024, 5)):
            # Petabyte
            size_string = "{0} PB".format(round(size / pow(1024, 5), 1))
        elif (size >= pow(1024, 4)):
            # Terabyte
            size_string = "{0} TB".format(round(size / pow(1024, 4), 1))
        elif (size >= pow(1024, 3)):
            # Gigabyte
            size_string = "{0} GB".format(round(size / pow(1024, 3), 1))
        elif (size >= pow(1024, 2)):
            # Megabyte
            size_string = "{0} MB".format(round(size / pow(1024, 2), 1))
        elif (size >= 1024):
            # Kilobyte
            size_string = "{0} KB".format(round(size / 1024, 1))

        return size_string

    def __push_keys_to_version(self, keys, dataset_id, version_id):
        payload = { 
            "keys" : keys,
            "versionId" : version_id
        }

        url = self.routes_controller.push_keys_to_version_url(dataset_id)
        return self.__api_post(url, payload)

    def upload_new_dataset(self, filepath, name, description, version_name="v1", version_message="Initial Upload", rows_limit=500000, scratch_directory="scratch", isPublic=False):
        """Creates a new dataaet and uploads a new version

        A two-birds-with-one-stone method for creating a new dataset on the Cortex web app
        and uploading a version from a CSV file

        Args:
            filepath (str): Path to a CSV file. IMPORTANT: the CSV file must have a header row. Also, the first column of the CSV must be named "index". It should enumerate each row of the dataset starting with 0 (e.g. 0, 1, 2, 3, 4, 5... N)
            name (str): Name for the new dataset
            description (str): Description for the new dataset
            version_name (str, optional): Name of the Dataset version
            version_message (str, optional): A message for the Dataset version. Think of it as a commit message in Git
            rows_limit (int, optional): Controls how many rows are allowed in one dataset chunk. Cortex partitions large datasets into smaller chunks for quicker queries. So if your `rows_limit` is set to 500000, then a 6M rows dataset will be split into 12 chunks
            scratch_directory (str, optional): A temporary scratch directory for splitting the dataset before upload
            isPublic (bool, optional): A flag indicating whether or not this dataset should be made public

         Returns:
            dict: A dictionary representing a newly created dataset

        Typical usage example:

            >>> filepath = "/path/to/my/dataset.csv"
            >>> dataset = client.upload_new_dataset(
                filepath, 
                "Iris Dataset", 
                "The legendary Iris dataset",
                isPublic=True)
            Dataset split into 1 parts                           
            [ Uploading Iris.csv - 4.8 KB ]
            [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||] - 100%
            Cleaning up...
            Upload complete!
            >>> print(dataset["_id"])
            62d72790365bad0016adea0c
        """
        dataset = self.create_dataset(name, description, isPublic)
        self.upload_dataset_version(filepath, dataset["_id"], version_name, version_message, rows_limit=rows_limit, scratch_directory=scratch_directory)
        return dataset

    def upload_dataset_version(self, filepath, dataset_id, version_name, version_message, rows_limit=500000, scratch_directory="scratch", check_header=True, make_current=True):
        """Upload a new version of an existing dataset

        Args:
            filepath (str): Path to a CSV file. IMPORTANT: the CSV file must have a header row. Also, the first column of the CSV must be named "index". It should enumerate each row of the dataset starting with 0 (e.g. 0, 1, 2, 3, 4, 5... N)
            dataset_id (str): ID of the dataset the version belongs to
            version_name (str): Name of the Dataset version
            version_message (str): A message for the Dataset version. Think of it as a commit message in Git
            rows_limit (int, optional): Controls how many rows are allowed in one dataset chunk. Cortex partitions large datasets into smaller chunks for quicker queries. So if your `rows_limit` is set to 500000, then a 6M rows dataset will be split into 12 chunks
            scratch_directory (str, optional): A temporary scratch directory for splitting the dataset before upload
            check_header (bool, optional): A flag indicating whether or not the CSV should be checked to make sure it has a header. Header checks are not 100% reliable, which is why you can disable it in case if a file with a valid header is being misidentified as headerless
            isPublic (bool, optional): A flag indicating whether or not this dataset should be made public

        Returns:
            dict: A dictionary containing the Version object and an S3 prefix for the uploaded CSV file

        Typical usage example:
            
            >>> path = "path/to/my/dataset/iris.csv"
            >>> dataset = client.get_dataset_by_name("iris")
            >>> client.upload_dataset_version(path, dataset["_id"], "Version 5", "Updated Jul 20, 2022")
        """
        filename = ntpath.basename(filepath)

        num_rows, headers = self.__validate_csv(filepath, check_header=check_header)

        mongo_version_result = self.__add_dataset_version(version_name, version_message, filename, dataset_id, num_rows, headers, make_current)

        prefix = mongo_version_result["prefix"]
        verson_id = mongo_version_result["version"]["_id"]

        size = os.path.getsize(filepath)
        
        size_string = self.__format_bytes(size)

        parts = self.__split_dataset(filepath, num_rows, rows_limit=rows_limit, scratch_directory=scratch_directory)
        keys = self.__get_part_keys(parts, prefix)

        
        print("[ Uploading {0} - {1} ]".format(ntpath.basename(filepath), size_string))
        index = 1
        total = len(keys)
        for part, key in zip(parts, keys):
            self.__single_part_upload(part, key)
            self.__print_progress_bar(total, index)
            index += 1

        self.__push_keys_to_version(keys, dataset_id, verson_id)
        print("Cleaning up...")
        self.__clean_up(scratch_directory)

        print("Upload complete!")

        return mongo_version_result



        # if (size < 30 * 1024 * 1024): # If less than 30 MB
        #     self.__single_part_upload(filepath, key)
        # else:
        #     self.__multi_part_upload(filepath, key, bucket, max_size=max_chunk_size)
    def make_version_current(self, datasetId, versionId):
        """Marks an existing dataset version as current

        Current version is returned by default when the dataset is downloaded or accessed
        through a `cortex.cortex_cursor.CortexCursor` object

        Args:
            datasetId (str): ID of the target dataset
            versionId (str): ID of the version that belongs to the dataset

        Returns:
            dict: A dictionary representing an updated dataset

        Typical usage example:
            
            >>> dataset = client.get_dataset_by_name("iris")
            >>> client.list_dataset_versions(dataset["_id"])
            Dataset [62bd73700cb1eb5a281e872f] versions:
            [ ]  v1      [62bd73740cb1eb5a281e8736] 	 2022-06-30T09:57:08.456Z
            [ ]  v2      [62a8b7e7fbbf6c6afd311eb3]      2022-07-12T05:11:17.243Z
            [+]  v3      [62a8f780ee68522bd4280869]      2022-07-15T01:45:21.437Z
            >>> client.make_version_current(dataset["_id"], "62bd73740cb1eb5a281e8736")
            >>> client.list_dataset_versions(dataset["_id"])
            [+]  v1      [62bd73740cb1eb5a281e8736] 	 2022-06-30T09:57:08.456Z
            [ ]  v2      [62a8b7e7fbbf6c6afd311eb3]      2022-07-12T05:11:17.243Z
            [ ]  v3      [62a8f780ee68522bd4280869]      2022-07-15T01:45:21.437Z
        """
        url = self.routes_controller.make_version_current_url(datasetId)
        payload = {
            "versionId": versionId
        }

        return self.__api_post(url, payload)


    def __get_part_keys(self, parts, prefix):
        keys = []
        for p in parts:
            filename = ntpath.basename(p)
            keys.append(prefix + filename)

        return keys


    def __split_dataset(self, dataset_path, total_rows, rows_limit=500000, scratch_directory="scratch"):
        if not os.path.isdir(scratch_directory):
            os.makedirs(scratch_directory)

        paths = []

        current_min = 0
        current_max = rows_limit - 1

        index = 0

        name = os.path.join(scratch_directory, "{0}-{1}").format(current_min, current_max)
        paths.append(name)

        printed_line = "Splitting dataset... [ chunk {0:,}-{1:,} of {2:,} ]\r".format(current_min, current_max, total_rows)
        sys.stdout.write(printed_line)
        sys.stdout.flush()
        t = open(name, "a")

        with open(dataset_path, "r") as f:
            header = f.readline()
            t.write(header)

            while True:
                line = f.readline()
                if not line:
                    break

                if index <= current_max:
                    t.write(line)
                else:
                    t.close()
                    current_min += rows_limit
                    current_max += rows_limit

                    name = os.path.join(scratch_directory, "{0}-{1}").format(current_min, current_max)
                    paths.append(name)

                    printed_line = "Splitting dataset... [ chunk {0:,}-{1:,} of {2:,} ]\r".format(current_min, current_max, total_rows)

                    sys.stdout.write(printed_line)
                    sys.stdout.flush()

                    t = open(name, "a")
                    t.write(header)
                    t.write(line)

                index += 1
        t.close()
        sys.stdout.write(" " * (len(printed_line) + 5) + "\r")
        sys.stdout.write("Dataset split into {0} parts\n".format(len(paths)))
        sys.stdout.flush()
        return paths

    def __clean_up(self, scratch_directory):
        try:
            shutil.rmtree(scratch_directory)
        except OSError as e:
            print("Unable to clean up scratch directory")
        

    def __validate_csv(self, filepath, check_header=True):
        num_rows = -1 # Excluding the header
        
        with open(filepath, "r") as f:
            for _ in f:
                num_rows += 1

        if check_header:
            with open(filepath, 'r') as csvfile:
                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(csvfile.read(2048))
                if not has_header:
                    raise Exception("Your CSV file must have a header row")

        with open(filepath, "r") as f:
            header = f.readline()
            first_line = f.readline()
            second_line = f.readline()

            parsed_headers = list(csv.reader([header]))[0]

            header_one = parsed_headers[0]
            if header_one != "index":
                raise Exception("The first column of your dataset must be called \"index\". Values in the index column must start with 0 and enumerate every row of your data in sequence (e.g. 0, 1, 2, 3... {0})".format(num_rows))

            first_value = first_line.split(",")[0]
            second_value = second_line.split(",")[0]

            try:
                first_index = int(first_value)
                if first_index != 0:
                    raise Exception("Values in the index column must start with 0 and enumerate every row of your data in sequence (e.g. 0, 1, 2, 3... {0})".format(num_rows))
            except:
                    raise Exception("Values in the index column must start with 0 and enumerate every row of your data in sequence (e.g. 0, 1, 2, 3... {0})".format(num_rows))

            
            try:
                second_index = int(second_value)
                if second_index != 1:
                    raise Exception("Values in the index column must start with 0 and enumerate every row of your data in sequence (e.g. 0, 1, 2, 3... {0})".format(num_rows))
            except:
                raise Exception("Values in the index column must start with 0 and enumerate every row of your data in sequence (e.g. 0, 1, 2, 3... {0})".format(num_rows))

        return num_rows, parsed_headers
               



    def __get_dataset_download_urls(self, dataset_id):
        url = self.routes_controller.get_dataset_download_urls(dataset_id)
        return self.__api_get(url)


    def __get_download_key(self, key):
        payload = {
            "key" : key
        }
        url = self.routes_controller.get_download_key_url()
        return self.__api_post(url, payload)
        


    def __single_part_upload(self, filepath, key):
        signed_uris = self.__get_s3_signed_urls([key])
        signed = signed_uris[0]["url"]
        with open(filepath, 'rb') as f:
            contents = f.read()
            response = requests.put(signed, data=contents)
        if (response.status_code == 200):
            return True
        else:
            return False

    def __multi_part_upload(self, filepath, key, bucket, max_size=50*1024*1024):
        response = self.__create_multipart_upload(key)

        upload_id = response['UploadId']
        parts = []

        total_bytes = os.path.getsize(filepath)
        current_bytes = 0

        part_number = 1


        self.__print_progress_bar(total_bytes, current_bytes)
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(max_size)
                signed_url = self.__get_s3_signed_url_for_multipart_upload(key, upload_id=upload_id, part_number=part_number)
                response = requests.put(signed_url, data=chunk)
                etag = response.headers['ETag']
                parts.append({"ETag": etag, "PartNumber":part_number})
                part_number += 1
                current_bytes += sys.getsizeof(chunk)
                self.__print_progress_bar(total_bytes, current_bytes)
                if not chunk:
                    # EOF reached, end loop
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    break
        response = self.__complete_multipart_upload(key, {'Parts': parts}, upload_id)
        print("Upload complete")

    def __print_progress_bar(self, total_bytes, current_bytes):
        percentage = math.ceil(current_bytes / total_bytes * 100)
        if percentage > 100:
            percentage = 100
        bars = "|" * percentage
        spaces = " " * (100 - percentage)
        bar = "[{0}{1}] - {2}%".format(bars, spaces, percentage)
        if current_bytes != total_bytes:
            sys.stdout.write(bar + '\r')
        else:
            sys.stdout.write(bar + '\n')
        sys.stdout.flush()

    
    # SAGEMAKER
    def __deploy_endpoint(
        self, 
        run_id, 
        url,
        additional_params = {},
        wait_till_done=False):

        run = self.get_run_by_id(run_id)

        version = run["libraryVersion"]
        

        payload = {
            "run_id" : run_id,
            "flavor" : run["library"]["name"],
            "flavor_version" : version,
            "key" : run["metadata"]["s3_key"]
        }

        for key in additional_params:
            payload[key] = additional_params[key]

        response = self.__api_post(url, payload)

        if (wait_till_done):
            result = self.describe_endpoint(run_id)
            while result["EndpointStatus"] == "Creating" or result["EndpointStatus"] == "NotDeployed":
                time.sleep(15)
                result = self.describe_endpoint(run_id)

        return response

    def deploy_dedicated_endpoint(
        self, 
        run_id, 
        region="us-east-1",
        instance_type="ml.t2.medium",
        wait_till_done=False):

        """Deploys a dedicated Sagemaker endpoint serving a logged Run

        Dedicated endpoints are quite expensive to run and by default regular users do not have
        the rights to deploy dedicated instances. If you would like to deploy dedicated
        endpoints, you should talk to one of CORE admins

        Args:
            run_id (str): ID of the Run to deploy
            region (str, optional): AWS region
            instance_type (str, optional): Sagemaker instance type (see the full list of [Sagemaker Instance Types](https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-available-instance-types.html))
            wait_till_done (bool, optional): A flag determining whether the method should start the deployment process and return, or wait until deployment finishes
        
        Returns:
            dict: A dictionary showing the deployment status

        Typical usage example:

            >>> run_id = "62a8f780ee68522bd4280869"
            >>> result = client.deploy_dedicated_endpoint(run_id)
            >>> print(result)
            {
                "EndpointName": "62a8f780ee68522bd4280869",
                "EndpointStatus": "Creating",
                "EndpointType": "dedicated",
            }
        """

        params = {
            "region_name" : region,
            "instance_type" : instance_type,
        }

        url = self.routes_controller.deploy_dedicated_endpoint_url()
        response = self.__deploy_endpoint(run_id, url, params, wait_till_done)
        return response



    def deploy_serverless_endpoint(
        self, 
        run_id,
        memory_size=2048,
        max_concurrency=5,
        instance_type="ml.t2.medium",
        wait_till_done=False):

        """Deploys a serverless Sagemaker endpoint serving a logged Run

        Serverless endpoints are a very cost-effective way to deploy ML models compared
        to dedicated instances. One drawback of serverless inference however is the fact
        that an endpoint that hasn't been used for a period of time automatically goes to sleep.
        The following invocation then results in what's known as a "cold start", where the endpoint
        needs to wake up and warm up before returning the result. The duration of the cold start
        varies depending on the size of the model. Usually it ranges from around 10 - 30 seconds. All
        subsequent requests are returned with no additional latency.

        Args:
            run_id (str): ID of the Run to deploy
            memory_size (int): The size of available memory for a serverless instance. Available options are `1024` MB, `2048` MB, `3072` MB, `4096` MB, `5120` MB, or `6144` MB
            max_concurrency (int): Maximum number of allowed concurrent invocations for the scaling policy. The upper limit of allowed concurrent invocations is `200`
            instance_type (str, optional): Sagemaker instance type (see the full list of [Sagemaker Instance Types](https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-available-instance-types.html))
            wait_till_done (bool, optional): A flag determining whether the method should start the deployment process and return, or wait until deployment finishes

        Returns:
            dict: A dictionary showing the deployment status

        Typical usage example:
            
            >>> run_id = "62a8f780ee68522bd4280869"
            >>> result = client.deploy_serverless_endpoint(run_id)
            >>> print(result)
            {
                "EndpointName": "62a8f780ee68522bd4280869",
                "EndpointStatus": "Creating",
                "EndpointType": "serverless",
            }
        """

        params = {
            "memory_size": memory_size,
            "max_concurrency": max_concurrency,
            "instance_type": instance_type
        }

        url = self.routes_controller.deploy_serverless_endpoint_url()
        response = self.__deploy_endpoint(run_id, url, params, wait_till_done)
        return response

    def delete_endpoint(self, run_id):
        """Deletes a deployed endpoint

        Args:
            run_id (str): ID of the Run that was deployed through that endpoint

        Returns:
            dict: A dictionary indicating the success of the delete operation

        Typical usage example:
            
            >>> run_id = "62a8f780ee68522bd4280869"
            >>> result = client.delete_endpoint(run_id)
            >>> print(result)
            { "success": True }
        """
        url = self.routes_controller.delete_endpoint_url(run_id)
        return self.__api_delete(url)

    def describe_endpoint(self, run_id):
        """Returns metadata for a deployed Sagemaker endpoint

        Args:
            run_id (str): ID of a logged Run

        Returns:
            dict: A dictionary with endpoint metadata

        Typical usage example:
            
            >>> run_id = "62a8f780ee68522bd4280869"
            >>> metadata = client.describe_endpoint(run_id)
            >>> print(metadata)
            {
                "EndpointName": "62a8f780ee68522bd4280869",
                "EndpointArn": "arn:aws:sagemaker..."
                "EndpointConfigName": "62a8f780ee68522bd4280869",
                "ProductionVariants": [
                {
                    "VariantName": "pytorchVariant",
                    "DeployedImages": [...],
                    "CurrentWeight": 1,
                    "DesiredWeight": 1,
                    "CurrentInstanceCount": 0
                }
            ],
                "EndpointStatus": "InService",
                "CreationTime": "2022-07-15T08:13:18.361Z",
                "LastModifiedTime": "2022-07-15T08:15:38.226Z"
            }

        """
        url = self.routes_controller.describe_endpoint_url(run_id)
        return self.__api_get(url)

    def invoke_run(self, run_id, data, contentType="application/json"):
        """Invokes a deployed endpoint via the Run ID

        Args:
            run_id (str): ID of the Run served by the endpoint
            data (any): Depending on the deployed model, it will be either a `dict`, a `list` or a `csv string` with input data for inference
            contentType (str, optional): Data content type

        Returns:
            any: Inference results

        Typical usage example:

            >>> run_id = "62a8f780ee68522bd4280869"
            >>> data = {"inputs": [[7, 5, 160, 0]]}
            >>> result = client.invoke_run(run_id, data)
            >>> print(result)
            "0.9083"
        """
        payload = {
            "run_id": run_id,
            "input_data": data,
            "content_type": contentType
        }

        url = self.routes_controller.invoke_endpoint_url()
        return self.__api_post(url, payload)

    def invoke_model(self, model_id, data, contentType="application/json"):
        """Invokes a deployed endpoint via the Model ID

        Args:
            model_id (str): ID of the Model that exposes a deployed Run
            data (object): Depending on the deployed model, it will be either a `dict`, a `list` or a `csv string` with input data for inference
            contentType (str, optional): Data content type

        Returns:
            object: Inference results

        Typical usage example:

            >>> model_id = "62a8f780ee68522bd4280869"
            >>> data = {"inputs": [[7, 5, 160, 0]]}
            >>> result = client.invoke_model(model_id, data)
            >>> print(result)
            "0.9083"
        """
        payload = {
            "model_id": model_id,
            "input_data": data,
            "content_type": contentType
        }

        url = self.routes_controller.invoke_endpoint_url()
        return self.__api_post(url, payload)

    def delete_run(self, run_id):
        """Deletes a logged Run

        If a logged Run is deployed to an endpoint, this method will throw an error

        Args:
            run_id (str): ID of the logged Run to delete

        Returns:
            dict: A dictionary indicating the success of the delete operation

        Typical usage examples:
            
            >>> run_id = "62a8f780ee68522bd4280869"
            >>> result = client.delete_run(run_id)
            >>> print(result)
            { "deleted": True }
        """
        url = self.routes_controller.delete_run_url(run_id)
        return self.__api_delete(url)

    def delete_experiment(self, experiment_id):
        """Deletes a Cortex Experiment

        If an Experiment contains deployed Runs, this method will throw an error

        Args:
            experiment_id (str): ID of the Experiment to delete

        Returns:
            dict: A dictionary indicating the success of the delete operation

        Typical usage examples:
            
            >>> exp = client.get_experiment_by_name("Timber")
            >>> result = client.delete_experiment(exp["_id"])
            >>> print(result)
            { "deleted": True }
        """
        url = self.routes_controller.delete_experiment_url(experiment_id)
        return self.__api_delete(url)


if __name__ == "__main__":
    with open("secret.json", 'r') as f:
        credentials = json.load(f)


    client = CortexClient(
        cortex_token=credentials["cortex_token"],
        #endpoint="https://cortex-pr-131.herokuapp.com"
        endpoint="http://localhost:1337/"
    )



    


