"""Calculate simple descreptive stats from csv with Python with cli or  import respecting the limit of 512 MB """

import sys
from importlib import metadata as importlib_metadata

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata

def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
