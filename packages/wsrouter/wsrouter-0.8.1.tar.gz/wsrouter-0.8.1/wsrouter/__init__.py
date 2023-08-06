from importlib import metadata

# Single source the version string from package metadata
__version__ = metadata.version(__package__)

del metadata  # avoids polluting the results of dir(__package__)

from .router import WebSocketRouter
from .router import WebSocketRouterEndpoint
from .message import WebSocketMessageEndpoint
from .cmd import WebSocketCommandEndpont
from .cmd import command
