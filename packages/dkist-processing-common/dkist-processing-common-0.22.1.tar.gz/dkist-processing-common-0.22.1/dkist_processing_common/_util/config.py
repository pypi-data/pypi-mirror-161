"""Helper functions for retrieving configurations."""
import json
from collections import defaultdict
from os import environ
from typing import Union


def get_config(
    key: str, default: Union[None, bool, str, dict, list, int, float] = None, is_json: bool = False
) -> Union[None, bool, str, dict, list, int, float]:
    """
    Get configuration information from the specified environment variable.

    Parameters
    ----------
    key
        The environment variable from which to read the configuration.
    default
        The default value to be used if the environment variable is not defined.
    is_json
        Boolean to determine if the value should be returned as a json object or not

    Returns
    -------
    The configuration specified by the given environment variable.
    """
    value = environ.get(key, default)
    if is_json:
        return json.loads(value)
    return value


def get_mesh_config(default: str = "null") -> dict:
    """
    Get the MESH_CONFIG environment variable.

    MESH_CONFIG is an environment variable indicating how to connect to dependencies on the service mesh

    Parameters
    ----------
    default
        The default value to be used if MESH_CONFIG is not defined.

    Returns
    -------
    The value of the MECH_CONFIG environment variable
    """
    MESH_CONFIG = get_config("MESH_CONFIG", default=default, is_json=True)
    host_port_default = {"mesh_address": "localhost", "mesh_port": 5672}
    mesh_default = defaultdict(lambda: host_port_default, {})
    MESH_CONFIG = MESH_CONFIG or mesh_default
    return MESH_CONFIG
