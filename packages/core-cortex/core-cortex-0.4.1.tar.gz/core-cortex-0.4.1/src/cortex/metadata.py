"""Contains classes used for model tracking

This module contains a number of classes that support logging model
hyperparameters, metrics and other metadata
"""

class LogEntry:
    """A class representing a logged entry (either a hyperparameter or a model metric)

    This class is NOT meant to be instantiated explicitly. It is instantiated via
    logging methods inside of the `cortex.cortex.CortexClient` object such as 
    `cortex.cortex.CortexClient.log_param` or `cortex.cortex.CortexClient.log_metric`

    Args:
        name (str): Entry name
        value (any): Entry value as `str`, `int`, `float` or `bool`
        epoch (int, optional): The number of the current epoch if the value is logged in a loop

    Typical usage example:
        
        >>> client.log_metric("acc", accuracy)
    """
    def __init__(self, name, value, epoch=0):
        self.name = name
        self.__validate_type(value)
        self.value = value
        self.epoch = epoch

    def __validate_type(self, value):
        if not isinstance(value, str) and \
           not isinstance(value, int) and \
           not isinstance(value, float) and \
           not isinstance(value, bool):

           raise Exception("Logged values must be of type String, Integer, Float or Boolean")

    def toDict(self):
        """Converts an instance of `LogEntry` to a Python `dict` (not meant to be called explicitly)

        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible by other classes during upload to the database
        """
        d = {
            self.epoch : [
                {
                    "name": self.name,
                    "value": self.value
                }
            ]
        }
        return d


class Metadata:
    """A class containing model metadata

    This class is NOT meant to be instantiated explicitly. Its instance is created
    when a model is logged to the tracking server through `cortex.cortex.CortexClient`

    Args:
        params (list of `LogEntry`, optional): Logged parameters
        metrics (list of `LogEntry`, optional): Logged metrics
        s3_key (str, optional): S3 key of uploaded model assets
    """
    def __init__(self, params=[], metrics=[], s3_key=""):
        self.parameters = params
        """Logged parameters"""
        self.metrics = metrics
        """Logged metrics"""
        self.s3_key = s3_key
        """S3 key of uploaded model assets"""

    def log_param(self, param: LogEntry):
        """Adds a `LoggedEntry` object to the `parameters` collection (not meant to be called explicitly)
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible by other classes during upload to the database
        """
        self.parameters.append(param)

    def log_metric(self, metric: LogEntry):
        """Adds a `LoggedEntry` object to the `metrics` collection (not meant to be called explicitly)
        
        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible by other classes during upload to the database"""
        self.metrics.append(metric)

    def toDict(self):
        """Converts an instance of `Metadata` to a Python `dict` (not meant to be called explicitly)

        This method is not meant to be called explicitly. The only reason why it was not made private
        via the `_` prefix, is because it has to be accessible by other classes during upload to the database"""
        metrics = {}

        for m in self.metrics:
            mDict = m.toDict()
            epoch = m.epoch
            dataList = mDict[epoch]

            if epoch in metrics:
                metrics[epoch].extend(dataList)
            else:
                metrics[epoch] = dataList

        params = {}

        for p in self.parameters:
            pDict = p.toDict()
            epoch = p.epoch
            dataList = pDict[epoch]

            if epoch in params:
                params[epoch].extend(dataList)

            else:
                params[epoch] = dataList

        metadata = {
            "metrics" : metrics,
            "parameters" : params,
            "s3_key": self.s3_key
        }

        return metadata

