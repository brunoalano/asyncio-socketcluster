"""
The :mod:`asyncio_socketcluster.client` module defines a simple WebSocket
client API.

"""

import asyncio
import websockets
from .protocol import SocketClusterCommonProtocol

class SocketClusterClientProtocol(SocketClusterCommonProtocol):
  """
  Complete WebSocket client implementation as an :class:`asyncio.Protocol`.
  This class inherits most of its methods from

  :class:`~asyncio_socketcluster.protocol.SocketClusterCommonProtocol`.

  """
  is_client = True
  side = 'client'

  def __init__(self, *args, **kwargs):
    super(SocketClusterClientProtocol, self).__init__(*args, **kwargs)