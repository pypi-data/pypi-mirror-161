from typing import Callable, Tuple
from inspect import isasyncgenfunction, isgeneratorfunction
import asyncio

from .message import Message, MessageType

from .request import Request
from .utils import encode, decode
from .app import App

import logging

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, app: App) -> None:
        self.__host = app._host
        self.__endpoints = app.endpoints

    async def _connection_factory(
        self,
    ) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        if isinstance(self.__host, tuple):
            host, port = self.__host
            return await asyncio.open_connection(host=host, port=port)
        else:
            return await asyncio.open_unix_connection(self.__host)

    async def start_request(self, name, args, kwargs):
        request = Request(name, *args, **kwargs)
        reader, writer = await self._connection_factory()
        logger.debug(f"Connected to {name}")
        writer.write(encode(request))
        await writer.drain()
        return reader, writer

    def __getattr__(self, __name: str) -> Callable:
        if not __name in self.__endpoints.keys():
            raise Exception("No such endpoint!")

        if isasyncgenfunction(self.__endpoints[__name]) or isgeneratorfunction(
            self.__endpoints[__name]
        ):

            async def handler_generator(*args, **kwargs):
                reader, writer = await self.start_request(__name, args, kwargs)
                try:
                    writer.write(
                        encode(Message(MessageType.generator_request, None))
                    )
                    await writer.drain()
                    async for line in reader:
                        msg = decode(line)
                        match msg.type:
                            case MessageType.exception:
                                raise msg.content
                            case MessageType.generator_result:
                                yield msg.content
                            case other:
                                raise Exception("Unknown answer")
                        writer.write(
                            encode(Message(MessageType.generator_request, None))
                        )
                        await writer.drain()
                finally:
                    writer.write_eof()
                    await writer.drain()

            handler_generator.__annotations__ = self.__endpoints[
                __name
            ].__annotations__
            handler_generator.__name__ = __name
            handler_generator.__qualname__ = __name
            return handler_generator
        else:

            async def handler(*args, **kwargs):
                reader, writer = await self.start_request(__name, args, kwargs)
                msg = decode(await reader.readline())
                try:
                    match msg.type:
                        case MessageType.function_result:
                            return msg.content
                        case MessageType.exception:
                            raise msg.content
                        case other:
                            raise Exception("Unknown answer")
                finally:
                    writer.write_eof()
                    await writer.drain()

            handler.__annotations__ = self.__endpoints[__name].__annotations__
            handler.__name__ = __name
            handler.__qualname__ = __name
            return handler
