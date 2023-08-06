import os

class VersionError(Exception):
    """
    Version Too Low
    """
class NoneInstrumentError(Exception):
    """
    Instrument does not exist
    """
class ConfigError(Exception):
    """
    _config.json damaged
    """
class LostModuleError(Exception):
    """
    Imcomplete modules
    """
class UnknownArgError(Exception):
    """
    False Args
    """