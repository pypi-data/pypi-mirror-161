"""Contains instrumentation for dataset traversal

This module contains the `CortexCursor` object that lets you programmatically
query datasets in Cortex's Data Store
"""

import requests
import json

class CortexCursor(object):
    """Cursor object for dataset traversal

    This class is NOT meant to be instantiated explicitly. Instead
    use the `cortex.cortex.CortexClient.get_dataset_cursor` method.

    Args:
        server (string): IP or URL of the Cortex server
        dataset (dict): A dictionary representing a Dataset object
        auth_headers (dict): A dictionary of auth headers

    Typical usage example:

        >>> client = CortexClient("MY_CORTEX_TOKEN_HERE") 
        >>> dataset = client.get_dataset_by_name("iris")
        >>> cursor = client.get_dataset_cursor(dataset["_id"])
        >>> done = False
        >>> while not done:
                batch, done = cursor.fetch_next(num_rows=512)
                // do stuff with the batch
    """
    def __init__(self, server, dataset, auth_headers):
        self.__metadata = dataset
        self.__num_rows = dataset["currentVersion"]["totalRows"]
        self.__dataset_id = dataset["_id"]
        self.__version_id = dataset["currentVersion"]["_id"]

        self.__headers = auth_headers

        self.reset()

        # Routes
        self.__server = server
        self.__top_url = "{0}/api/dataset/{1}/top".format(self.__server, self.__dataset_id)
        self.__header_url = "{0}/api/dataset/{1}/get-header".format(self.__server, self.__dataset_id)
        self.__range_url = "{0}/api/dataset/{1}/get-range".format(self.__server, self.__dataset_id)

    def reset(self):
        """Resets the counter back to the beginning

        Typical usage example:

            >>> dataset = client.get_dataset_by_name("timber")
            >>> cursor = client.get_dataset_cursor(dataset["_id"])
            >>> done = False
            >>> while not done:
                    batch, done = cursor.fetch_next(num_rows=512)
                    // do stuff with the batch
            >>> cursor.reset()
        """
        self.__last_fetched_index = -1

    def __get(self, url, params={}):
        if params != {}:
            url += "?"
            for k in params:
                value = params[k]
                url += "{0}={1}&".format(k, value)
            url = url[:-1]
        result = requests.get(url, headers=self.__headers)
        if result.status_code == 200:
            return result
        else:
            print("HTTP code:", result.status_code)
            print("Reason:", result.reason)
            print("Text:", result.text)
            raise Exception("Server returned an error")

    def __post(self, url, payload):
        result = requests.post(url, data=json.dumps(payload), headers=self.__headers)
        if result.status_code == 200:
            return result
        else:
            print("HTTP code:", result.status_code)
            print("Reason:", result.reason)
            print("Text:", result.text)
            raise Exception("Server returned an error")

    def __api_post(self, url, payload):
        response = self.__post(url, payload)
        return self.__unpack_response(response.text)


    def __api_get(self, url):
        response = self.__get(url)
        return self.__unpack_response(response.text)

    def __unpack_response(self, response:str):
        data = json.loads(response)
        if (data["error"] != None):
            raise Exception(data["message"])
        else:
            return data["data"]

    def total_rows(self):
        """Returns the total number of rows in a dataset

        Returns:
            int: Total number of rows not including the header

        Typical usage example:
            
            >>> n_rows = cursor.total_rows()
            >>> print(n_rows)
            45809
        """
        return self.__num_rows

    def header(self):
        """Returns a list of column names for a dataset (dataset header)
        
        Returns:
            list of str: Dataset column names

        Typical usage example:
            
            >>> headers = cursor.header()
            >>> print(headers)
            ["index", "sepal_len_cm", "sepal_width_cm", "petal_len_cm", "petal_width_cm", "class"]
        """
        header_list = self.__api_get(self.__header_url)
        return header_list

    def top(self, num_rows=20):
        """Gets the top N rows of a dataset

        Args:
            num_rows (int, optional): Number of top rows to return

        Returns:
            list of list: Dataset rows

        Typical usage example:

            >>> top_rows = cursor.top(num_rows=100)
            >>> print(top_rows)
            100
        """
        payload = {
            "numRows": num_rows
        }

        t = self.__api_post(self.__top_url, payload)
        
        t.remove([])
        return t

    def fetch_next(self, num_rows=1024, select_columns = []):
        """Fetches consecutive batches of dataset rows

        Args:
            num_rows (int, optional): Number of rows per batch
            select_columns (list of str, optional): Columns to fetch. If no columns are provided, all columns will be returned

        Returns:
            list of list: A batch of dataset rows
            bool: A boolean indicating whether the end of the dataset has been reached

        Typical usage example:
            
            >>> dataset = client.get_dataset_by_name("timber")
            >>> cursor = client.get_dataset_cursor(dataset["_id"])
            >>> done = False
            >>> while not done:
                    batch, done = cursor.fetch_next(num_rows=512)
                    // do stuff with the batch
        """
        done = False
        start = self.__last_fetched_index + 1
        end = start + num_rows

        payload = {
            "startRow" : start,
            "endRow" : end,
            "columns" : select_columns
        }
        
        batch = self.__api_post(self.__range_url, payload)
        if [] in batch:
            batch.remove([])
        self.__last_fetched_index = end - 1
        
        if self.__last_fetched_index - 1 >= self.__num_rows:
            done = True
        return self.__postprocess_table(batch), done

    def dataset_version_id(self):
        """Returns the ID of the selected dataset version

        Returns:
            str: Selected dataset version ID

        Typical usage example:
            
            >>> dataset = client.get_dataset_by_name("iris")
            >>> client.list_dataset_versions(dataset["_id"])
            Dataset [62bd73700cb1eb5a281e872f] versions:
            [ ]  v1      [62bd73740cb1eb5a281e8736] 	 2022-06-30T09:57:08.456Z
            [ ]  v2      [62a8b7e7fbbf6c6afd311eb3]      2022-07-12T05:11:17.243Z
            [+]  v3      [62a8f780ee68522bd4280869]      2022-07-15T01:45:21.437Z
            >>> cursor = client.get_dataset_cursor(dataset["_id"])
            >>> print(cursor.dataset_version_id())
            62a8f780ee68522bd4280869
        """
        return self.__version_id

    def __postprocess_table(self, table):
        postprocessed = []
        for a in table:
            postprocessed.append(self.__postprocess_array(a))
        return postprocessed
        
    def __postprocess_array(self, array):
        new_array = []
        for value in array:
            try:
                # as float
                new_array.append(float(value))
            except:
                try:
                    # as int
                    new_array.append(int(value))
                except:
                    # as array
                    new_array.append(value)
        return new_array