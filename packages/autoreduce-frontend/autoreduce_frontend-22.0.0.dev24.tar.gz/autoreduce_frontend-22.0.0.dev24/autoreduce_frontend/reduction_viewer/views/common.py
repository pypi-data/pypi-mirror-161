import base64
import itertools
import json
from typing import Tuple
from autoreduce_db.reduction_viewer.models import ReductionArguments
from autoreduce_qp.queue_processor.variable_utils import VariableUtils

UNAUTHORIZED_MESSAGE = "User is not authorized to submit batch runs. Please contact the Autoreduce team "\
                       "at ISISREDUCE@stfc.ac.uk to request the permissions."
# Holds the default value used when there is no value for the variable
# in the default variables dictionary. Stored in a parameter for re-use in tests.
DEFAULT_WHEN_NO_VALUE = ""


def _combine_dicts(current: dict, default: dict):
    """
    Combine the current and default variable dictionaries, into a single
    dictionary which can be more easily rendered into the webapp.

    If no current variables are provided, return the default as both current and
    default.
    """
    if not current:
        current = default.copy()

    final = {}
    for name in itertools.chain(current.keys(), default.keys()):
        # the default value for argument, also used when the variable is missing from the current variables
        # ideally there will always be a default for each variable name, but
        # if the variable is missing from the default dictionary, then just default to empty string
        default_value = default.get(name, DEFAULT_WHEN_NO_VALUE)
        final[name] = {"current": current.get(name, default_value), "default": default_value}

    return final


def unpack_arguments(arguments: dict) -> Tuple[dict, dict, dict]:
    """
    Unpacks an arguments dictionary into separate dictionaries for
    standard, advanced variables, and variable help.

    Args:
        arguments: The arguments dictionary to unpack.

    Returns:
        A tuple containing the standard variables, advanced variables, and variable help.
    """
    standard_arguments = arguments.get("standard_vars", {})
    advanced_arguments = arguments.get("advanced_vars", {})
    variable_help = arguments.get("variable_help", {"standard_vars": {}, "advanced_vars": {}})
    return standard_arguments, advanced_arguments, variable_help


def get_arguments_from_file(instrument: str) -> Tuple[dict, dict, dict]:
    """
    Loads the default variables from the instrument's reduce_vars file.

    Args:
        instrument: The instrument to load the variables for.

    Raises:
        FileNotFoundError: If the instrument's reduce_vars file is not found.
        ImportError: If the instrument's reduce_vars file contains an import error.
        SyntaxError: If the instrument's reduce_vars file contains a syntax error.
    """
    default_variables = VariableUtils.get_default_variables(instrument)
    default_standard_variables, default_advanced_variables, variable_help = unpack_arguments(default_variables)
    return default_standard_variables, default_advanced_variables, variable_help


def prepare_arguments_for_render(arguments: ReductionArguments, instrument: str) -> Tuple[dict, dict, dict]:
    """
    Converts the arguments into a dictionary containing their "current" and "default" values.

    Used to render the form in the webapp (with values from "current"), and
    provide the defaults for resetting (with values from "default").

    Args:
        arguments: The arguments to convert.
        instrument: The instrument to get the default variables for.

    Returns:
        A dictionary containing the arguments and their current and default values.
    """
    vars_kwargs = arguments.as_dict()
    standard_vars = vars_kwargs.get("standard_vars", {})
    advanced_vars = vars_kwargs.get("advanced_vars", {})

    default_standard_variables, default_advanced_variables, variable_help = get_arguments_from_file(instrument)

    final_standard = _combine_dicts(standard_vars, default_standard_variables)
    final_advanced = _combine_dicts(advanced_vars, default_advanced_variables)

    return final_standard, final_advanced, variable_help


def decode_b64(value: str):
    """
    Decodes the base64 representation back to utf-8 string.
    """
    return base64.urlsafe_b64decode(value).decode("utf-8")


# pylint:disable=too-many-return-statements
def convert_to_python_type(value: str):
    """
    Converts the string sent by the POST request to a real Python type that can be serialized by JSON

    Args:
        value: The string value to convert

    Returns:
        The converted value
    """
    try:
        # json can directly load str/int/floats and lists of them
        return json.loads(value)
    except json.JSONDecodeError:
        if value.lower() == "none" or value.lower() == "null":
            return None
        elif value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif "," in value and "[" not in value and "]" not in value:
            return convert_to_python_type(f"[{value}]")
        elif "'" in value:
            return convert_to_python_type(value.replace("'", '"'))
        else:
            return value


def make_reduction_arguments(post_arguments: dict, instrument: str) -> dict:
    """
    Given new variables from the POST request and the default variables from reduce_vars.py
    create a dictionary of the new variables

    Args:
        post_arguments: The new variables to be created
        default_variables: The default variables

    Returns:
        The new variables as a dict

    Raises:
        ValueError if any variable values exceed the allowed maximum
    """

    defaults = VariableUtils.get_default_variables(instrument)

    for key, value in post_arguments:
        if 'var-' in key:
            if 'var-advanced-' in key:
                name = key.replace('var-advanced-', '')
                dict_key = "advanced_vars"
            elif 'var-standard-' in key:
                name = key.replace('var-standard-', '')
                dict_key = "standard_vars"
            else:
                continue

            if name is not None:
                name = decode_b64(name)
                # skips variables that have been removed from the defaults
                if name not in defaults[dict_key]:
                    continue

                defaults[dict_key][name] = convert_to_python_type(value)
    return defaults
