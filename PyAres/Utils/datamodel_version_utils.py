from importlib import metadata

_DATAMODEL_DIST_NAME = "ares_datamodel"
_HEADER_NAME = "datamodel-version"


def get_datamodel_version() -> str:
    """
    Returns the installed version of the ares_datamodel package.

    Falls back to ares_datamodel.__version__ if the distribution metadata
    is not available, and finally to "unknown" if the package cannot be imported.
    """
    try:
        return metadata.version(_DATAMODEL_DIST_NAME)
    except metadata.PackageNotFoundError:
        try:
            import ares_datamodel  # type: ignore

            return getattr(ares_datamodel, "__version__", "unknown")
        except ImportError:
            return "unknown"


def get_datamodel_metadata_header() -> tuple[str, str]:
    """
    Returns the (key, value) tuple for the outgoing gRPC metadata header.
    """
    return _HEADER_NAME, get_datamodel_version()