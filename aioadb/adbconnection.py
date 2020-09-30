import asyncio
import dataclasses

from .adbexceptions import AdbResponseError

@dataclasses.dataclass
class Stream:
    reader: asyncio.StreamReader = None
    writer: asyncio.StreamWriter = None

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
       
    async def write(self, data: str):
        self.writer.write(self._serialize(data))
        await self.writer.drain()
    
    async def read_bytes(self, num_bytes: int) -> bytes:
        data = await self.reader.readexactly(num_bytes)
        return data

    async def read_until_close(self) -> bytes:
        content = b''
        while True:
            try:
                chunk = await self.reader.read()
                if not chunk:
                    break
                content += chunk
            except Exception as e:
                print(str(e))

            return content

    async def check_adb_response(self, value: bytes, bytes_to_read: int = 4):
        data = await self.read_bytes(bytes_to_read)
        try:
            assert data == value
        except AssertionError:
            AdbResponseError(f'Adb response unexpected: {data}')

    @staticmethod
    def _serialize(content: str) -> bytes:
        """Little endian format"""
        return "{:04x}{}".format(len(content), content).encode("utf-8")


class AdbConnection:

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self.stream = Stream()

    async def _create_connection(self):
        return await asyncio.open_connection(self._host, self._port)

    async def connect(self):
        self.stream.reader, self.stream.writer = await self._create_connection()