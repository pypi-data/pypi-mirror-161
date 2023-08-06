# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""
This script is modified based on [aml_adapter.py](https://eemo.visualstudio.com/TEE/_git/TEEGit?path=/Offline/GIS/src/libraries/gis-common-argument/gis/common/argument/aml_adapter.py)
"""
import logging
import re
from argparse import ArgumentParser, Namespace
from typing import Dict, Union
from ruamel.yaml import YAML

from shrike.compliant_logging.exceptions import (
    PublicArgumentTypeError,
    PublicTypeError,
    PublicRuntimeError,
)
from shrike.compliant_logging import DataCategory


def str_to_bool(val: Union[bool, str]) -> bool:
    """
    Resolving boolean arguments if they are not given in the standard format

    Arguments:
        val (bool or string): boolean argument type
    Output:
        bool: the desired value {True, False}

    """
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        if val.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif val.lower() in ("no", "false", "f", "n", "0"):
            return False
    raise PublicArgumentTypeError("Boolean value expected.")


TYPE_MAPPING = {
    "String": str,
    "string": str,
    "AnyDirectory": str,
    "Integer": int,
    "integer": int,
    "int": int,
    "Boolean": str_to_bool,
    "boolean": str_to_bool,
    "Bool": str_to_bool,
    "bool": str_to_bool,
    "Float": float,
    "float": float,
    "Enum": str,
    "enum": str,
    "path": str,
}


def get_args_from_component_spec(
    component_spec_file_name: str, logger: logging.Logger
) -> Namespace:
    """create and apply the ArgumentParser based on component_spec_file_name

    Parameters
    ----------
    component_spec_file_name: the file name of component spec

    Returns
    -------
    args parsed from command
    """
    try:
        logger.info(
            "======== Parsing input arguments ========", category=DataCategory.PUBLIC
        )
    except TypeError:
        # TypeError: _log() got an unexpected keyword argument 'category'
        raise PublicTypeError(
            "The auto arg parser API only works with [category-aware logging](https://shrike-docs.com/compliant_logging/). Please call `enable_compliant_logging()` before creating a logger."
        )

    with open(component_spec_file_name, mode="r", encoding="utf-8") as stream:
        spec = YAML(typ="safe").load(stream)
        command_str = ""
        if "command" in spec:
            command_str = spec["command"]
        elif "hdinsight" in spec:
            command_str = spec["hdinsight"]["args"]
        elif "launcher" in spec:
            command_str = spec["launcher"]["additional_arguments"]
        elif "parallel" in spec:
            command_str = spec["parallel"]["args"]

        logger.info(command_str, category=DataCategory.PUBLIC)
        parser = _create_argument_parser(
            command_str, spec["inputs"], spec.get("outputs", None)
        )
    args, _ = parser.parse_known_args()
    _log_args(args, logger)

    return args


def _log_args(args: Namespace, logger: logging.Logger = None) -> None:
    """log the arguments for the debugging purpose"""
    logger.info(
        "======== Arguments from command ========", category=DataCategory.PUBLIC
    )
    for name, value in vars(args).items():
        logger.info("name=%s, value=%s" % (name, value), category=DataCategory.PUBLIC)


def _create_argument_parser(
    command: str, inputs: Dict[str, Dict[str, str]], outputs: Dict[str, Dict[str, str]]
) -> ArgumentParser:
    """create the argument parser from component spec: command, inputs and outputs"""
    parser = ArgumentParser()
    command_dict = _parse_command(command)

    for arg_name, arg_setting in command_dict.items():
        inputs_or_outputs, field = arg_setting.strip().split(".")
        if inputs_or_outputs == "inputs":
            _add_argument(parser, arg_name, inputs[field])
        elif inputs_or_outputs == "outputs":
            _add_argument(parser, arg_name, outputs[field])
        else:
            raise PublicRuntimeError("unknown fields in spec command")

    return parser


def _parse_command(command: str) -> Dict[str, str]:
    """parse the command to dict: key is the optional argument,
    value is either inputs or outputs

    Examples
    --------
    command = 'python3 run.py --input {inputs.input_path} --input_file {inputs.input_file} --output {outputs.output_file}
    [--apply {inputs.apply}] [--select {inputs.select}]'

    return = {'--input': 'inputs.input_path', '--input_file': 'inputs.input_file', '--output': 'outputs.output_file',
              '--apply': 'inputs.apply', '--select': 'inputs.select'}
    """
    pattern = r"(--[a-zA-Z0-9_]+)\s+\{([a-zA-Z0-9\._]+)\}"
    matches = re.findall(pattern, command)
    return dict(matches)


def _add_argument(
    parser: ArgumentParser, argument_name: str, setting: Dict[str, str]
) -> None:
    """mapping from AML component spec keywords to `add_argument` keywords:

    description -> help
    optional -> required
    type -> type
    default -> default
    enum -> choices
    """
    help_info = setting.get("description", "no help info for this argument")
    setting_type = setting.get("type", "String")
    type_ = TYPE_MAPPING.get(setting_type, str)
    required = False if setting.get("optional", False) else True
    default_value = setting.get("default", None)
    choices = setting.get("enum", None)

    parser.add_argument(
        argument_name,
        required=required,
        type=type_,
        help=help_info,
        default=default_value,
        choices=choices,
    )
