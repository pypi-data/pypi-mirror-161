# -*- coding: utf-8 -*-
from pathlib import Path


def get_current_file_directory(the_file: str) -> Path:
    """ Wrapper to get path to current file directory.
    
    This is a simple abstraction to avoid calling the returned sequence
    everytime. This is useful to handling load of internal configuration
    files in packages. Simply call with `__file__` as argument.

    Parameters
    ----------
    the_file : str
        File to have its parent path determined, generally magic
        string `__file__` in packages.

    Returns
    -------
    Path
        The resolved parent path of required file.
    """
    return Path(the_file).resolve().parent


def get_configuration_file(the_file: str, conf_relative_path: str) -> Path:
    """ Wrapper to get path of a configuration file relative to parent.
    
    Parameters
    ----------
    the_file : str
        File to have its parent path determined, generally magic
        string `__file__` in packages.
    conf_relative_path : str
        Relative path of configuration file from parent directory.

    Returns
    -------
    Path
        The resolved path of required configuration file.
    """
    return get_current_file_directory(the_file) / conf_relative_path
