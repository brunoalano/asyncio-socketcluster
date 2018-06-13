import asyncio
import pytest
import websockets
import asyncio_socketcluster

@pytest.mark.asyncio
async def test_client_connection():
  ws_url = "wss://localhost:8000/socketcluster/"
  async with websockets.connect(ws_url) as websocket:
    pong_waiter = await websocket.send("hello")
    assert await pong_waiter is not None
