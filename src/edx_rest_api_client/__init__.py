from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("edx-rest-api-client")
except PackageNotFoundError:  # pragma: no cover
    pass
