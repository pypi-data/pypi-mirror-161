"""Provide high-level UDP endpoints for asyncio.

Originally from: https://gist.github.com/vxgmichel/e47bff34b68adb3cf6bd4845c4bed448

"""

__all__ = ["open_local_endpoint", "open_remote_endpoint"]

import asyncio
import logging

_LOG = logging.getLogger(__name__)


class DatagramEndpointProtocol(asyncio.DatagramProtocol):
    """Datagram protocol for the endpoint high-level interface."""

    def __init__(self, endpoint):
        self._endpoint = endpoint

    # Protocol methods

    def connection_made(self, transport):
        self._endpoint._transport = transport

    def connection_lost(self, exc):
        assert exc is None
        if self._endpoint._write_ready_future is not None:
            self._endpoint._write_ready_future.set_result(None)
        self._endpoint.close()

    # Datagram protocol methods

    def datagram_received(self, data, addr):
        self._endpoint.feed_datagram(data, addr)

    def error_received(self, exc):
        _LOG.warning("Endpoint received an error: %s", repr(exc))

    # Workflow control

    def pause_writing(self):
        assert self._endpoint._write_ready_future is None
        loop = self._endpoint._transport._loop
        self._endpoint._write_ready_future = loop.create_future()

    def resume_writing(self):
        assert self._endpoint._write_ready_future is not None
        self._endpoint._write_ready_future.set_result(None)
        self._endpoint._write_ready_future = None


# Enpoint classes


class Endpoint:
    """High-level interface for UDP enpoints.

    Can either be local or remote.
    It is initialized with an optional queue size for the incoming datagrams.
    """

    def __init__(self, queue_size=None):
        if queue_size is None:
            queue_size = 0
        self._queue = asyncio.Queue(queue_size)
        self._closed = False
        self._transport = None
        self._write_ready_future = None

    # Protocol callbacks

    def feed_datagram(self, data, addr):
        try:
            self._queue.put_nowait((data, addr))
        except asyncio.QueueFull:
            _LOG.warning("Endpoint queue is full")

    def close(self):
        # Manage flag
        if self._closed:
            return
        self._closed = True
        # Wake up
        if self._queue.empty():
            self.feed_datagram(None, None)
        # Close transport
        if self._transport:
            self._transport.close()

    # User methods

    def send(self, data, addr):
        """Send a datagram to the given address."""
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.sendto(data, addr)

    async def receive(self):
        """Wait for an incoming datagram and return it with
        the corresponding address.

        This method is a coroutine.
        """
        if self._queue.empty() and self._closed:
            raise IOError("Enpoint is closed")
        data, addr = await self._queue.get()
        if data is None:
            raise IOError("Enpoint is closed")
        return data, addr

    def abort(self):
        """Close the transport immediately."""
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.abort()
        self.close()

    async def drain(self):
        """Drain the transport buffer below the low-water mark."""
        if self._write_ready_future is not None:
            await self._write_ready_future

    # Properties

    @property
    def address(self):
        """The endpoint address as a (host, port) tuple."""
        return self._transport.get_extra_info("socket").getsockname()

    @property
    def closed(self):
        """Indicates whether the endpoint is closed or not."""
        return self._closed


class LocalEndpoint(Endpoint):
    """High-level interface for UDP local enpoints.

    It is initialized with an optional queue size for the incoming datagrams.
    """

    pass


class RemoteEndpoint(Endpoint):
    """High-level interface for UDP remote enpoints.

    It is initialized with an optional queue size for the incoming datagrams.
    """

    def send(self, data):
        """Send a datagram to the remote host."""
        super().send(data, None)

    async def receive(self):
        """Wait for an incoming datagram from the remote host.

        This method is a coroutine.
        """
        data, addr = await super().receive()
        return data


# High-level coroutines


async def open_datagram_endpoint(
    host, port, *, endpoint_factory=Endpoint, remote=False, loop=None, **kwargs
):
    """Open and return a datagram endpoint.

    The default endpoint factory is the Endpoint class.
    The endpoint can be made local or remote using the remote argument.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    if loop is None:
        loop = asyncio.get_event_loop()
    endpoint = endpoint_factory()
    kwargs["remote_addr" if remote else "local_addr"] = host, port
    kwargs["protocol_factory"] = lambda: DatagramEndpointProtocol(endpoint)
    await loop.create_datagram_endpoint(**kwargs)
    return endpoint


async def open_local_endpoint(
    host="0.0.0.0", port=0, *, queue_size=None, loop=None, **kwargs
):
    """Open and return a local datagram endpoint.

    An optional queue size arguement can be provided.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    return await open_datagram_endpoint(
        host,
        port,
        remote=False,
        endpoint_factory=lambda: LocalEndpoint(queue_size),
        loop=loop,
        **kwargs
    )


async def open_remote_endpoint(host, port, *, queue_size=None, loop=None, **kwargs):
    """Open and return a remote datagram endpoint.

    An optional queue size arguement can be provided.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    return await open_datagram_endpoint(
        host,
        port,
        remote=True,
        endpoint_factory=lambda: RemoteEndpoint(queue_size),
        loop=loop,
        **kwargs
    )
