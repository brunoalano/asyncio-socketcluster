"""
The :mod:`asyncio_socketcluster.protocol` module handles WebSocket control and
data based on RFC and SocketCluster Protocol.

"""

import json
import asyncio
import websockets
from websockets.protocol import State
from websockets.framing import *

class SocketClusterCommonProtocol(websockets.protocol.WebSocketCommonProtocol):
  # There are only two differences between the client-side and the server-
  # side behavior: masking the payload and closing the underlying TCP
  # connection. Set is_client and side to pick a side.
  is_client = None
  side = 'undefined'

  def __init__(self, *args, **kwargs):
    # initialize the base class
    super(SocketClusterCommonProtocol, self).__init__(*args, **kwargs)
    self._ws_counter = 0

  def ws_increment(self):
    self._ws_counter += 1
    return self._ws_counter

  def connection_open(self):
    """
    Callback when the WebSocket opening handshake completes.

    Enter the OPEN state and start the data transfer phase.

    """

    # 4.1. The WebSocket Connection is Established.
    assert self.state is State.CONNECTING
    self.state = State.OPEN

    # Start the task that receives incoming WebSocket messages.
    self.transfer_data_task = asyncio.ensure_future(
      self.transfer_data(), loop=self.loop)

    # Start the task that eventually closes the TCP connection.
    self.close_connection_task = asyncio.ensure_future(
    self.close_connection(), loop=self.loop)

    # Send a handshake
    handshake_obj = {
      "event": "#handshake",
      "data": {
        "authToken": None
      },
      "cid": self.ws_increment()
    }
    asyncio.ensure_future(self.send(json.dumps(handshake_obj)), loop=self.loop)

  async def read_data_frame(self, max_size):
    """
    Read a single data frame from the connection.

    Process control frames received before the next data frame.

    Return ``None`` if a close frame is encountered before any data frame.

    """

    # 6.2. Receiving Data
    while True:
      frame = await self.read_frame(max_size)

      # 5.5. Control Frames
      if frame.opcode == OP_CLOSE:

        # 7.1.5.  The WebSocket Connection Close Code
        # 7.1.6.  The WebSocket Connection Close Reason
        self.close_code, self.close_reason = parse_close(frame.data)
        # Echo the original data instead of re-serializing it with
        # serialize_close() because that fails when the close frame is
        # empty and parse_close() synthetizes a 1005 close code.
        await self.write_close_frame(frame.data)
        return

      elif frame.opcode == OP_PING:
        # Answer pings.
        # Replace by frame.data.hex() when dropping Python < 3.5.
        ping_hex = binascii.hexlify(frame.data).decode() or '[empty]'
        logger.debug("%s - received ping, sending pong: %s",
                     self.side, ping_hex)
        await self.pong(frame.data)

      elif frame.opcode == OP_PONG:
        # Acknowledge pings on solicited pongs.
        if frame.data in self.pings:
          # Acknowledge all pings up to the one matching this pong.
          ping_id = None
          ping_ids = []
          while ping_id != frame.data:
            ping_id, pong_waiter = self.pings.popitem(0)
            ping_ids.append(ping_id)
            pong_waiter.set_result(None)
          pong_hex = (binascii.hexlify(frame.data).decode() or '[empty]')
          logger.debug("%s - received solicited pong: %s",
                       self.side, pong_hex)
          ping_ids = ping_ids[:-1]
          if ping_ids:
            pings_hex = ', '.join(
              binascii.hexlify(ping_id).decode() or '[empty]'
              for ping_id in ping_ids
            )
            plural = 's' if len(ping_ids) > 1 else ''
            logger.debug("%s - acknowledged previous ping%s: %s",
              self.side, plural, pings_hex)
        else:
          pong_hex = (binascii.hexlify(frame.data).decode() or '[empty]')
          logger.debug("%s - received unsolicited pong: %s",
                         self.side, pong_hex)

      # 5.6. Data Frames
      else:
        return frame


  async def emit(self, event_name: str, obj):
    """
    This coroutine sends a message.

    It sends :class:`str` as a text frame and :class:`bytes` as a binary
    frame. It raises a :exc:`TypeError` for other inputs.

    """
    await self.ensure_open()
    emit_obj = {
      "event": event_name,
      "data": obj,
      "cid": self.ws_increment()
    }
    res = await self.send(json.dumps(emit_obj, sort_keys=True))
