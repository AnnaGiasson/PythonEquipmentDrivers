import pyvisa.errors


class UnsupportedResourceError(pyvisa.errors.Error):
    def __init__(self, message="Device is not supported", *args):
        super().__init__(message, *args)


class ResourceConnectionError(pyvisa.errors.Error):
    def __init__(self, message="Could not connect to device", *args):
        super().__init__(message, *args)
