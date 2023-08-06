"""
Hoppr utility functions
"""

import importlib
import inspect
import json
import os
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any, List

import yaml
from yaml.parser import ParserError as YamlParserError
from yaml.scanner import ScannerError as YAMLScannerError

from hoppr.context import Context
from hoppr.exceptions import HopprLoadDataError, HopprPluginError


def _class_in_module(obj, module):
    """
    Determines if the specified object is a class
    defined in the module
    """
    if not inspect.isclass(obj):
        return False

    module_source_string = inspect.getsource(module)
    class_source_string = inspect.getsource(obj)

    if class_source_string not in module_source_string:
        return False

    return True


def plugin_instance(plugin_name, context: Context, config: Any = None):
    """
    Create an instance of an object defined by a plugin name

    Assumes the specified plugin will define exactly one concrete class, which
    will be instaniated using a default constructor (i.e., one with no parameters).
    """

    try:
        plugin = importlib.import_module(plugin_name)
    except ModuleNotFoundError as mnfe:
        raise ModuleNotFoundError(
            f"Unable to locate plug-in {plugin_name}: {mnfe}"
        ) from mnfe

    plugin_obj = None

    for name, obj in inspect.getmembers(plugin):
        if _class_in_module(obj, plugin):

            if plugin_obj is not None:
                raise HopprPluginError(
                    f"Multiple candidate classes defined in {plugin_name}: "
                    + f"{plugin_obj.__name__}, {name}"
                )

            plugin_obj = obj

    if plugin_obj is None:
        raise HopprPluginError(f"No class definition found in in {plugin_name}.")

    return plugin_obj(context=context, config=config)


def load_string(contents: str):
    """
    Try loading yaml, json, and xml files into a dict.
    """
    try:
        return_value = yaml.safe_load(contents)

        ### yaml.safe_load will sometimes return a single string rather than
        ### the required structure.  Treating that as a failure

        if not isinstance(return_value, str):
            return return_value
    except (YamlParserError, YAMLScannerError):
        pass

    try:
        return json.loads(contents)
    except JSONDecodeError:
        pass

    raise HopprLoadDataError("Unable to recognize data as either json or yaml")


def load_file(input_file_path: Path):
    """
    Load file content (either json or yml) into a dict
    """

    if not input_file_path.is_file():
        raise HopprLoadDataError(f"{input_file_path} is not a file, cannot be opened.")

    with open(input_file_path, "r", encoding="utf-8") as input_file:
        content = input_file.read()
        return load_string(content)


def dedup_list(list_in: List[Any]) -> List[Any]:
    """
    De-duplicate a list
    """
    return list(dict.fromkeys(list_in)) if list_in is not None else []


def obscure_passwords(command_list, lst):
    """
    Returns an input string with any specified passwords hidden
    """

    command = ""
    for arg in command_list:
        if len(command) > 0:
            command += " "
        if " " in arg:
            command += f'"{arg}"'
        else:
            command += arg

    if lst is not None:
        for password in lst:
            if password is not None:
                command = command.replace(password, "<PASSWORD HIDDEN>")

    return command


def remove_empty(directory):
    """
    removes empty folders given the directory including parent folders
    """
    deleted = set()
    if not os.path.exists(directory):
        raise FileNotFoundError()
    for current_dir, subdirs, files in os.walk(directory, topdown=False):

        still_has_subdirs = any(
            subdir
            for subdir in subdirs
            if os.path.join(current_dir, subdir) not in deleted
        )

        if not any(files) and not still_has_subdirs:
            os.rmdir(current_dir)
            deleted.add(current_dir)

    return deleted
