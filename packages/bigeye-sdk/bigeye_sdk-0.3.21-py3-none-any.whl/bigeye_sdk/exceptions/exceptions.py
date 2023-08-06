class InvalidConfigurationException(Exception):
    def __init__(self, message: str):
        self.message = message


class BrowserAuthException(Exception):
    def __init__(self, message: str):
        self.message = message


class FeatureNotSupportedException(Exception):
    def __init__(self, message: str):
        self.message = message


class TagNotExistsException(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidMetricDefinitionException(Exception):
    def __init__(self, message: str):
        self.message = message

class NoColumnSelectorsDefinedException(Exception):
    def __init__(self, message: str):
        self.message = message


class SavedMetricIdNotExistsException(Exception):
    def __init__(self, message: str):
        self.message = message


class DuplicateIDExistsException(Exception):
    def __init__(self, message: str):
        self.message = message


class ConfigurationValidationException(Exception):
    def __init__(self, message: str):
        self.message = message
