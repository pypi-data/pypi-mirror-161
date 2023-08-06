# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Shared utils.
"""
import logging
import base64
from functools import wraps

log = logging.getLogger(__name__)


def experimental(
    message="This is an experimental feature and could change at any time.",
):
    def wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            log.warning(message)
            return func(*args, **kwargs)

        return new_func

    return wrapper


def b64_encode(s: str, encoding: str = "ascii") -> str:
    """
    Produce base-64 encoded version of `s`.
    """
    s_bytes = s.encode(encoding)
    b64_bytes = base64.b64encode(s_bytes)
    s_encoded = b64_bytes.decode(encoding)
    return s_encoded


def b64_decode(s: str, encoding: str = "ascii") -> str:
    """
    Return str corresponding to base-64 decoded, YAML
    deserialized, version of `s`.
    """
    b64_bytes = s.encode(encoding)
    s_bytes = base64.b64decode(b64_bytes)
    s_decoded = s_bytes.decode(encoding)
    return s_decoded
