"""
The :mod:`asyncio_socketcluster.protocol` module handles WebSocket control and
data based on RFC and SocketCluster Protocol.

"""

import asyncio
import websockets

class SocketClusterCommonProtocol(websockets.protocol.WebSocketCommonProtocol):
  # There are only two differences between the client-side and the server-
  # side behavior: masking the payload and closing the underlying TCP
  # connection. Set is_client and side to pick a side.
  is_client = None
  side = 'undefined'

  def __init__(self, *args, **kwargs):
    # initialize the base class
    super(SocketClusterCommonProtocol, self).__init__(*args, **kwargs)