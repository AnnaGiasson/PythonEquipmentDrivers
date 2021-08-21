
class UnsupportedResourceError(Exception):
    def __init__(self, message="Device is not supported", *args):
        super().__init__(message, *args)


class ResourceConnectionError(Exception):
    def __init__(self, message="Could not connect to device", *args):
        super().__init__(message, *args)


class EnvironmentSetupError(Exception):
    def __init__(self, message="Error configurating Environment", *args):
        super().__init__(message, *args)
