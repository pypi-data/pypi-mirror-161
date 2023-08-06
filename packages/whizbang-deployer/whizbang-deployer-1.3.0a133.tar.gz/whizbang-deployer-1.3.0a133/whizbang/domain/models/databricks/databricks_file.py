class DatabricksFile:
    def __init__(self,  source_path: str, destination_path: str, overwrite: bool):
        self.source_path = source_path
        self.destination_path = destination_path
        self.overwrite = overwrite
