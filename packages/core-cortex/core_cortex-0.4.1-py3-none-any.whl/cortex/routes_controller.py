"""Contains a utility class for accessing backend routes"""

class RoutesController():
    """A utility class for accessing backend routes

    This class is NOT meant to be instantiated on its own. An instance of the `RoutesController` 
    is automatically created with each new `CortexClient`
    """
    def __init__(self, server, auth_headers):
        self.server = server
        self.auth_headers = auth_headers
    
    # AUTH
    def sso_auth(self):
        """Returns the URL for authenticating to the SSO server"""
        return "https://coresso.thorntontomasetti.com/api/users/authenticate"

    def cortex_auth(self):
        """Returns the URL for authenticating to the Cortex web app"""
        return "{0}/api/authenticate/ssotoken".format(self.server)

    def validate_token(self):
        """Returns the URL for validating a Cortex access token"""
        return "{0}/api/public/validate-token".format(self.server)

    # CREATE
    def new_run_url(self):
        """Returns the URL for creating a new Run object in the database"""
        return "{0}/api/runs/new".format(self.server)

    def new_model_url(self):
        """Returns the URL for creating a new Model object in the database"""
        return "{0}/api/models/new".format(self.server)

    def new_experiment_url(self):
        """Returns the URL for creating a new Experiment object in the database"""
        return "{0}/api/projects/new".format(self.server)

    def create_multipart_upload(self):
        """Returns the URL for performing a multipart S3 upload"""
        return "{0}/api/datasets/create-multipart-upload".format(self.server)

    def complete_multipart_upload(self):
        """Returns the URL for completing a multipart S3 upload"""
        return "{0}/api/datasets/complete-multipart-upload".format(self.server)

    def create_dataset(self):
        """Returns the URL for creating a Dataset object in the database"""
        return "{0}/api/datasets/new-dataset".format(self.server)

    def create_dataset_version(self, dataset_id):
        """Returns the URL for creating a DatasetVersion object in the database"""
        return "{0}/api/dataset/{1}/add-version".format(self.server, dataset_id)


    # GET
    def get_all_projects_url(self):
        """Returns the URL for getting all projects accessible to the user"""
        return "{0}/api/projects/get-all".format(self.server)

    def get_project_info_url(self, projectId):
        """Returns the URL for getting Experiment metadata"""
        return "{0}/api/project/{1}/info".format(self.server, projectId)

    def get_projects_by_name_url(self):
        """Returns the URL for searching Experiments by name"""
        return "{0}/api/projects/get-by-name".format(self.server)

    def get_model_info_url(self, modelId):
        """Returns the URL for getting Model metadata"""
        return "{0}/api/model/{1}/info".format(self.server, modelId)

    def get_run_info_url(self, runId):
        """Returns the URL for getting Run metadata"""
        return "{0}/api/run/{1}/info".format(self.server, runId)

    def get_s3_bucket_url(self):
        """Returns the URL for getting the S3 bucket"""
        return "{0}/api/sagemaker/get-bucket".format(self.server)

    def get_s3_signed_urls(self):
        """Returns the URL for obtaining a signed URL for S3 upload"""
        return "{0}/api/runs/get-s3-signed-urls".format(self.server)

    def get_s3_signed_url_for_multipart_upload(self):
        """Returns the URL for  obtaining a signed URL for multipart S3 upload"""
        return "{0}/api/datasets/get-s3-signed-url-for-multipart-upload".format(self.server)

    def get_my_datasets_url(self):
        """Returns the URL for getting User's datasets"""
        return "{0}/api/datasets/get-my-datasets".format(self.server)

    def get_multiple_datasets_by_name_url(self):
        """Returns the URL for searching multiple datasets by dataset name"""
        return "{0}/api/datasets/get-multiple-by-name".format(self.server)

    def get_one_dataset_by_name_url(self):
        """Returns the URL for searching for a dataset by its name"""
        return "{0}/api/datasets/get-one-by-name".format(self.server)

    def get_dataset_by_id_url(self, id):
        """Returns the URL for getting a dataset via its ID"""
        return "{0}/api/dataset/{1}/info".format(self.server, id)

    def list_dataset_versions_url(self, id):
        """Returns the URL for listing dataset versions"""
        return "{0}/api/dataset/{1}/versions".format(self.server, id)

    def get_dataset_download_urls(self, id):
        """Returns the URL for getting a dataset's download links"""
        return "{0}/api/dataset/{1}/download-urls".format(self.server, id)

    def get_download_key_url(self):
        """Returns the URL for getting its S3 key"""
        return "{0}/api/datasets/get-download-url".format(self.server)

    def get_library_info(self, id):
        """Returns the URL for fetching ML library info"""
        return "{0}/api/library/{1}/info".format(self.server, id)


    # MODIFY
    def assign_run_url(self, modelId):
        """Returns the URL for assigning a Run to a Model"""
        return "{0}/api/model/{1}/assign-run".format(self.server, modelId)

    def update_payload_key(self, runId):
        """Returns the URL for updating the payload key of a newly created Run"""
        return "{0}/api/run/{1}/update-payload-key".format(self.server, runId)

    def push_keys_to_version_url(self, dataset_id):
        """Returns the URL for pushing S3 keys to the DatasetVersion object after the S3 upload has been complete"""
        return "{0}/api/dataset/{1}/push-keys-to-version".format(self.server, dataset_id)

    def make_version_current_url(self, dataset_id):
        """Returns the URL for assigning a dataset version as current"""
        return "{0}/api/dataset/{1}/assign-current-version".format(self.server, dataset_id)

    # SAGEMAKER
    def deploy_dedicated_endpoint_url(self):
        """Returns the URL for deploying a dedicated endpoint"""
        return "{0}/api/sagemaker/deploy-dedicated-endpoint".format(self.server)

    def deploy_serverless_endpoint_url(self):
        """Returns the URL for deploying a serverless endpoint"""
        return "{0}/api/sagemaker/deploy-serverless-endpoint".format(self.server)

    def delete_endpoint_url(self, run_id):
        """Returns the URL for  deleting an endpoint"""
        return "{0}/api/sagemaker/delete-endpoint/{1}".format(self.server, run_id)

    def invoke_endpoint_url(self):
        """Returns the URL for invoking an endpoint"""
        return "{0}/api/sagemaker/invoke-endpoint".format(self.server)

    def describe_endpoint_url(self, run_id):
        """Returns the URL for describing an endpoint"""
        return "{0}/api/sagemaker/describe-endpoint/{1}".format(self.server, run_id)

    def delete_run_url(self, run_id):
        """Returns the URL for deleting a Run"""
        print(run_id)
        return "{0}/api/sagemaker/delete-run/{1}".format(self.server, run_id)

    def delete_experiment_url(self, experiment_id):
        """Returns the URL for deleting an Experiment"""
        return "{0}/api/sagemaker/delete-experiment/{1}".format(self.server, experiment_id)

