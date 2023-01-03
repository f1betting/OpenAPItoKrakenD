class OpenAPIFileNotFoundError(FileNotFoundError):
    """
    Raised when there are no OpenAPI specs found in the input folder
    """
    def __init__(self, msg="No OpenAPI specs found"):
        super().__init__(msg)
