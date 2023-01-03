class InvalidOpenAPIError(ValueError):
    """
    Raised when the OpenAPI specification is invalid
    """
    def __init__(self, msg="Invalid OpenAPI specification"):
        super().__init__(msg)
