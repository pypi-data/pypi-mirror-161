# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module containing configuration functions. Configuration file must be used as a thread safe way to
share values between xdist workers does not currently exist.
"""
import json
import sys
from pathlib import Path
from shutil import copyfile

from autoreduce_utils.settings import AUTOREDUCE_HOME_ROOT

SELENIUM_CONFIG_DIR = Path(AUTOREDUCE_HOME_ROOT, "selenium_tests")
SELENIUM_CONFIG = Path(SELENIUM_CONFIG_DIR, "config.json")
TEMP_SELENIUM_CONFIG = Path(SELENIUM_CONFIG_DIR, "temp_config.json")

if not SELENIUM_CONFIG_DIR.exists():
    SELENIUM_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

if not SELENIUM_CONFIG.exists():
    SELENIUM_CONFIG.write_text("""{"url": "http://localhost:0000","run_headless": true}""", encoding="utf-8")


def store_original_config():
    """
    Make a copy of the config file to a temporary file. This prevents arguments given to the test
     entrypoint being persisted to the config file.
    """
    try:
        copyfile(SELENIUM_CONFIG, TEMP_SELENIUM_CONFIG)
    except OSError:
        sys.exit(f"Config file: {SELENIUM_CONFIG} could not be loaded...")


def get_url():
    """
    Returns the url to test against from the config
    :return: (str) The url to test against from the config
    """

    return load_config_file()["url"]


def is_headless():
    """
    Returns the headless boolean from the config
    :return: (bool) The headless boolean from the config
    """
    return load_config_file()["run_headless"]


def set_url(url):
    """
    Set the url to test against in the config. IPs must be prefixed with http/https still
    :param url: (str) The url to test against
    """
    config = load_config_file()
    config["url"] = url
    dump_to_config_file(config)


def set_headless(headless):
    """
    Set the headless option in the config to decide whether or not to use a headless driver
    :param headless: (bool) the headless bool option
    """
    config = load_config_file()
    config["run_headless"] = headless
    dump_to_config_file(config)


def cleanup_config():
    """
    Copy the original values back to the original config file, so as not to persist arguments given
    to test runner
    """
    copyfile(TEMP_SELENIUM_CONFIG, SELENIUM_CONFIG)
    if TEMP_SELENIUM_CONFIG.exists():
        TEMP_SELENIUM_CONFIG.unlink()


def load_config_file():
    """
    Load the config file into a python dictionary
    :return: (dict) The config file as a python dictionary
    """
    try:
        with open(SELENIUM_CONFIG, encoding='utf-8') as fle:
            return json.load(fle)
    except FileNotFoundError:
        sys.exit(f"Config file is missing. Please create: {str(SELENIUM_CONFIG)}")


def dump_to_config_file(config_dict):
    """
    Dump the given dictionary to the config file
    :param config_dict: (dict) the dictionary to be dumped.
    """
    with open(SELENIUM_CONFIG, mode="w", encoding='utf-8') as fle:
        json.dump(config_dict, fle, indent=4)
