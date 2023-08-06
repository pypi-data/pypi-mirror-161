"""Contains classes for inference I/O documentation

This module contains classes that let users define input and output schemas
for ML model inference. These schemas are displayed as logged Run metadata on
the web app and describe the data format required for model invocation, as
well as the expected format of inference results
"""

import numpy as np
import pandas as pd
import random

class TensorSpec:
    """Contains metadata of a tensor

    Used by the `CortexEntry` object to describe additional entry metadata in case
    if that entry is a tensor

    Args:
        dtype (numpy.dtype): Numpy data type of scalar values inside the tensor
        shape (list): Tensor shape
    """
    def __init__(
        self,
        dtype: np.dtype,
        shape: list):

        self.dtype = str(dtype)
        """Numpy data type of scalar values inside the tensor"""
        self.shape = shape
        """Tensor shape"""

    def toDict(self):
        """Converts an instance of `TensorSpec` to its dictionary representation
        
        Returns:
            dict: A dictionary representation of the `TensorSpec` instance
        """
        d = {
            "dataType": self.dtype,
            "shape": self.shape
        }
        return d

    @staticmethod
    def from_tensor(array: np.ndarray):
        return TensorSpec(array.dtype, list(array.shape))


class CortexEntry:
    """Describes an IO entry (essentially, a dataset column)
    
    Args:
        name (str): Entry name
        description (str): Entry description
        sample_value (any): Sample value for the entry
        tensor_spec (TensorSpec, optional): Optional `TensorSpec` in case the `CortexEntry` is a tensor

    Typical usage example:

        >>> signature = CortexSignature()
        >>> signature.addInput(CortexEntry("sepal_len_cm", "Sepal length in cm", 5.1))
    """
    def __init__(
        self, 
        name: str, 
        description: str,
        sample_value,
        tensor_spec: TensorSpec = None):

        self.name = name
        """Schema entry name"""
        self.type = type(sample_value).__name__
        """Schema entry data type (inferred automatically from the `sample_value`)"""
        self.description = description
        """Schema entry description"""
        self.tensorSpec = tensor_spec
        """Optional `TensorSpec` descriptor (if `CortexEntry` is a tensor)"""
        self.sampleValue = sample_value
        """Sample entry value"""

        if (self.tensorSpec != None):
            self.type = "tensor"

    def toDict(self):
        """Converts a `CortexEntry` instance to a dictionary representation
        
        Returns:
            dict: Dictionary representation of the `CortexEntry` instance
        """
        val = self.sampleValue
        try:
            # Make sure the value isn't
            # a numpy value that cannot
            # be serialized
            val = val.item()
        except:
            pass

        d = {
            "name": self.name,
            "dataType": self.type,
            "description": self.description,
            "sampleValue": val,
            "tensorSpec": None
        }

        if self.tensorSpec is not None:
            d["tensorSpec"] = self.tensorSpec.toDict()

        return d


class CortexSignature:
    """The main model schema object defining IO for a logged model

    Args:
        inputs (CortexEntry, optional): Input entries (dataset column definitions)
        outputs (CortexEntry, optional): Output entries (dataset column definitions)

    Typical usage example:
        
        >>> # Create a signature
        >>> signature = CortexSignature()
        >>> input_descriptions = [
                "Beam length in feet",
                "Beam spacing in feet",
                "Live load in psf",
                "Timber species"
            ]
        >>> output_descriptions = [
                "Beam profile section"
            ]
        >>> signature.inputs_from_dataframe(X, randomSample=True, descriptions=input_descriptions)
        >>> signature.outputs_from_dataframe(y, randomSample=True, descriptions=output_descriptions)
        >>> # Log model
        >>> run = client.pytorch.log_model(
            model,
            run_name = "Parameters, Metrics, Signature, Dataset",
            run_description = "Test run with Parameters, Metrics, Signature and Dataset",
            cortex_experiment_id = exp["_id"],
            signature = signature # Provide model signature
        )
    """
    def __init__(self, inputs=[], outputs=[]):
        self.inputs = inputs
        """Input `CortexEntry` objects"""
        self.outputs = outputs
        """Output `CortexEntry` objects"""

    def addInput(self, inp: CortexEntry):
        """Adds a `CortexEntry` object to the `CortexSignature.inputs` collection

        Args:
            inp (CortexEntry): Entry to add to the `CortexSignature.inputs` collection

        Typical usage example:

            >>> signature = CortexSignature()
            >>> signature.addInput(CortexEntry("sepal_len_cm", "Sepal length in cm", 5.1))
            >>> signature.addInput(CortexEntry("sepal_width_cm", "Sepal width in cm", 3.5))
            >>> signature.addInput(CortexEntry("petal_len_cm", "Petal length in cm", 1.4))
            >>> signature.addInput(CortexEntry("petal_width_cm", "Petal width in cm", 0.2))
        """
        self.inputs.append(inp)

    def addOutput(self, outp: CortexEntry):
        """Adds a `CortexEntry` object to the `CortexSignature.outputs` collection
        
        Args:
            outp (CortexEntry): Entry to add to the `CortexSignature.outputs` collection

        Typical usage example:

            >>> signature = CortexSignature()
            >>> signature.addOutput(CortexEntry("class", "Iris flower class", "Iris-setosa"))
        """
        self.outputs.append(outp)

    def toDict(self):
        """Converts an instance of a `CortexSignature` object to a dictionary representation

        Returns:
            dict: A dictionary representation of the `CortexSignature` instance
        """
        d = {
            "inputs" : [],
            "outputs" : []
        }

        for i in self.inputs:
            d["inputs"].append(i.toDict())

        for o in self.outputs:
            d["outputs"].append(o.toDict())

        return d


    def inputs_from_dataframe(self, df:pd.DataFrame, randomSample=False, descriptions=[]):
        """Parses model inputs from a Pandas dataframe the model has been trained on

        Parsed `CortexEntry` objects are added to the `CortexSignature.inputs` collection of the 
        `CortexSignature` instance that's calling the method
        
        Args:
            df (DataFrame): Pandas `DataFrame` that was used to train the model. The `DataFrame` should only contain input columns
            randomSample (bool, optional): A flag indicating whether a sample value for all `CortexEntry` objects should be picked from a random dataset row. If `False`, the value from the first row will be used
            descriptions (list of str, optional): A list of descriptions for each `CortexEntry`. The number of descriptions must match the number of colums in the input `DataFrame`

        Typical usage example:
            
            >>> signature = CortexSignature()
            >>> input_descriptions = [
                    "Beam length in feet",
                    "Beam spacing in feet",
                    "Live load in psf",
                    "Timber species"
                ]
            >>> signature.inputs_from_dataframe(X, randomSample=True, descriptions=input_descriptions)
        """
        self.inputs = []
        for e in self._parse_entries_from_df(df, randomSample, descriptions):
            self.addInput(e)

    def outputs_from_dataframe(self, df:pd.DataFrame, randomSample=False, descriptions=[]):
        """Parses model outputs from a Pandas dataframe the model has been trained on

        Parsed `CortexEntry` objects are added to the `CortexSignature.outputs` collection of the 
        `CortexSignature` instance that's calling the method
        
        Args:
            df (DataFrame): Pandas `DataFrame` that was used to train the model. The `DataFrame` should only contain output columns
            randomSample (bool, optional): A flag indicating whether a sample value for all `CortexEntry` objects should be picked from a random dataset row. If `False`, the value from the first row will be used
            descriptions (list of str, optional): A list of descriptions for each `CortexEntry`. The number of descriptions must match the number of colums in the output `DataFrame`

        Typical usage example:
            
            >>> signature = CortexSignature()
            >>> output_descriptions = [
                    "Beam profile section"
                ]
            >>> signature.outputs_from_dataframe(y, randomSample=True, descriptions=output_descriptions)
        """
        self.outputs = []
        for e in self._parse_entries_from_df(df, randomSample, descriptions):
            self.addOutput(e)

    def inputs_from_array(self, array:np.ndarray, headers:list, randomSample=False, descriptions=[]):
        """Parses model inputs from a Numpy array the model has been trained on

        Parsed `CortexEntry` objects are added to the `CortexSignature.inputs` collection of the 
        `CortexSignature` instance that's calling the method
        
        Args:
            array (ndarray): Numpy `ndarray` that was used to train the model. The `ndarray` should only contain input columns. Also, it **must have at least 2 dimensions**. If your array is 1D, you can fix it with `reshape(-1,1)`
            headers (list of str): Headers (column names) for model inputs.
            randomSample (bool, optional): A flag indicating whether a sample value for all `CortexEntry` objects should be picked from a random dataset row. If `False`, the value from the first row will be used
            descriptions (list of str, optional): A list of descriptions for each `CortexEntry`. The number of descriptions must match the number of colums in the input `ndarray`

        Typical usage example:
            
            >>> signature = CortexSignature()
            >>> input_headers = [
                    "beam_len_ft",
                    "beam_spacing_ft",
                    "ll_psf",
                    "species"
                ]
            >>> input_descriptions = [
                    "Beam length in feet",
                    "Beam spacing in feet",
                    "Live load in psf",
                    "Timber species"
                ]
            >>> signature.inputs_from_array(X, input_headers, randomSample=True, descriptions=input_descriptions)
        """
        self.inputs = []
        for e in self._parse_entries_from_array(array, headers, randomSample, descriptions):
            self.addInput(e)

    def outputs_from_array(self, array:np.ndarray, headers:list, randomSample=False, descriptions=[]):
        """Parses model outputs from a Numpy array the model has been trained on

        Parsed `CortexEntry` objects are added to the `CortexSignature.outputs` collection of the 
        `CortexSignature` instance that's calling the method
        
        Args:
            array (ndarray): Numpy `ndarray` that was used to train the model. The `ndarray` should only contain output columns. Also, it **must have at least 2 dimensions**. If your array is 1D, you can fix it with `reshape(-1,1)`
            headers (list of str): Headers (column names) for model outputs.
            randomSample (bool, optional): A flag indicating whether a sample value for all `CortexEntry` objects should be picked from a random dataset row. If `False`, the value from the first row will be used
            descriptions (list of str, optional): A list of descriptions for each `CortexEntry`. The number of descriptions must match the number of colums in the output `ndarray`

        Typical usage example:
            
            >>> signature = CortexSignature()
            >>> output_headers = [
                    "beam_sxn",
                ]
            >>> output_descriptions = [
                    "Beam profile section"
                ]
            >>> signature.outputs_from_array(y, output_headers, randomSample=True, descriptions=output_descriptions)
        """
        self.outputs = []
        for e in self._parse_entries_from_array(array, headers, randomSample, descriptions):
            self.addOutput(e)

    def _parse_entries_from_df(self, df:pd.DataFrame, randomSample=False, descriptions=[]):
        entries = []
        row = 0
        if randomSample:
            row = random.randint(0, df.shape[0])

        index = 0
        for (colname, coldata) in df.iteritems():
            description = colname
            if descriptions != [] and index < len(descriptions):
                description = descriptions[index]
            entry = CortexEntry(colname, description, coldata[row], None)
            entries.append(entry)
            index += 1
        
        return entries

    def _parse_entries_from_array(self, array: np.ndarray, headers: list, randomSample=False, descriptions=[]):
        if len(array.shape) < 2:
            raise Exception("Provided array of shape {0}. Input array must have at least two dimensions".format(array.shape))
        if array.shape[1] != len(headers):
            raise IndexError("Number of headers must match number of columns in array")
        
        entries = []
        row = 0
        if randomSample:
            row = random.randint(0, array.shape[0])

        index = 0
        array_row = array[row]
        for col, header in zip(array_row, headers):
            description = header
            if descriptions != [] and index < len(descriptions):
                description = descriptions[index]
            spec = TensorSpec(col.dtype, col.shape)
            if col.shape == ():
                spec = None
            else:
                col = list(col)
            entry = CortexEntry(header, description, col, spec)
            entries.append(entry)
            index += 1
            
        return entries