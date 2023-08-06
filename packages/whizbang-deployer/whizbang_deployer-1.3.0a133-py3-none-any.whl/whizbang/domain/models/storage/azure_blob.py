class AzureBlob:
    def __init__(self,
                 blob_name: str,
                 container_name: str,
                 account_name: str):
        self.blob_name = blob_name
        self.container_name = container_name
        self.account_name = account_name
