import os

from dotenv import load_dotenv


def comma_separated_string_to_array(ctx, param, value):
    """Split a non empty string and return the result list

    Or return an empty list if the value is empty string.
    """
    return value.split(",") if value else []


def load_env_from_config(conf_file="~/.qsentry/config"):
    return load_dotenv(os.path.expanduser(conf_file))
