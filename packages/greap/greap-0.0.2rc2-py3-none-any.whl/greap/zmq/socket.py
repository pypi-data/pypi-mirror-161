"""A Socket subclass that adds some serialization methods."""
import socket
from typing import Union, TypeVar, Type
import orjson

from typeguard import check_type, typechecked
import zmq
import zmq.asyncio

from ..types import DictSerializable, PrimitiveU
from ..immortals.signals import *  # noqa: F401,F403


ST = TypeVar("ST", zmq.Socket, zmq.asyncio.Socket)


def socket_factory(sock_cls: ST) -> Type[ST]:
    class S(sock_cls):
        def connect(self, addr):
            self.__dict__["addr"] = addr
            domain, port = addr[6:].split(":")
            new_addr = addr[:6] + socket.gethostbyname(domain) + ":" + port
            print("connect old_addr", addr)
            print("new_addr", new_addr)
            return super().connect(new_addr)

        def bind(self, addr):
            self.__dict__["addr"] = addr
            domain, port = addr[6:].split(":")
            new_addr = addr[:6] + "0.0.0.0" + ":" + port
            print("bind old_addr", addr)
            print("new_addr", new_addr)
            return super().bind(new_addr)

    return S


_Socket = socket_factory(zmq.Socket)
_AsyncSocket = socket_factory(zmq.asyncio.Socket)


class Socket(_Socket):
    @typechecked
    def send(self, obj: Union[PrimitiveU, DictSerializable]):
        if issubclass(type(obj), DictSerializable):
            obj = obj.to_dict()

        check_type(argname="obj", value=obj, expected_type=PrimitiveU)
        obj = orjson.dumps(obj)
        super().send(obj)

    def recv(self, noblock: bool = False) -> Union[PrimitiveU, DictSerializable]:
        if noblock:
            try:
                obj = super().recv(zmq.NOBLOCK)
            except zmq.error.Again:
                return None
        else:
            obj = super().recv()
        obj = orjson.loads(obj)
        try:
            obj = DictSerializable.from_dict(obj)
        except (ValueError, TypeError, KeyError):
            pass
        return obj


class AsyncSocket(_AsyncSocket):
    @typechecked
    async def send(self, obj: Union[PrimitiveU, DictSerializable]):
        if issubclass(type(obj), DictSerializable):
            obj = obj.to_dict()

        check_type(argname="obj", value=obj, expected_type=PrimitiveU)
        obj = orjson.dumps(obj)
        await super().send(obj)

    async def recv(self, noblock: bool = False) -> Union[PrimitiveU, DictSerializable]:
        if noblock:
            try:
                obj = await super().recv(zmq.NOBLOCK)
            except zmq.error.Again:
                return None
        else:
            obj = await super().recv()
        obj = orjson.loads(obj)
        try:
            obj = DictSerializable.from_dict(obj)
        except (ValueError, TypeError, KeyError):
            pass
        return obj


class Context(zmq.Context):
    _socket_class = Socket


class AsyncContext(zmq.Context):
    _socket_class = AsyncSocket
