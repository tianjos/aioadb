import asyncio

class AdbConnection:

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._reader = None
        self._writer = None

    async def _create_connection(self):
        return await asyncio.open_connection(self._host, self._port)

    async def _connect(self):
        self._reader, self._writer = await self._create_connection()

    
    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()
       
    async def write(self, data: str):
        self._writer.write(self._serialize(data))
        await self._writer.drain()
    
    async def read_bytes(self, num_bytes: int) -> bytes:
        data = await self._reader.readexactly(num_bytes)
        return data

    async def read_until_close(self) -> bytes:
        content = b''
        while True:
            try:
                chunk = await self._reader.read()
                if not chunk:
                    break
                content += chunk
            except Exception as e:
                print(str(e))

            return content

    @staticmethod
    def _serialize(content: str) -> bytes:
        """Little endian format"""
        return "{:04x}{}".format(len(content), content).encode("utf-8")
    
    
