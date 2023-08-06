class ConduitSDKError(Exception):
    pass


class ValidationError(ConduitSDKError):
    pass


class VaultError(ConduitSDKError):
    pass
