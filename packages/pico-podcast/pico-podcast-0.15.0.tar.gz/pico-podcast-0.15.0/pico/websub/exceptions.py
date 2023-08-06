class WebsubError(Exception):
    pass


class DiscoveryError(WebsubError):
    pass


class SubscriptionError(WebsubError):
    pass


class SignatureValidationError(WebsubError):
    pass
