from .adbconnection import AdbConnection, Stream
from .adbdevice import AdbDevice
from .adbsync import Sync

class AdbClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._adbconnection = AdbConnection(self._host, self._port)

    @property
    def sync(self) -> Sync:
        return Sync(self, self.serial)
    
    async def connect_to_adb(self):
        await self._adbconnection._connect()
    
    async def get_stream(self) -> Stream:
        return await self._adbconnection.stream()
    
    async def shell(self, serial: str, cmd: str):
        await self.connect_to_adb()
        await self._adbconnection.write(f'host:transport:{serial}')
        data = await self._adbconnection.read_bytes(4)
        assert data == b'OKAY'
        await self._adbconnection.write(f'shell: {cmd}')
        data = await self._adbconnection.read_bytes(4)
        assert data == b'OKAY'
        try:
            data = await self._adbconnection.read_until_close()
            return data
        except Exception as e:
            print(e)
        finally:
            await self._adbconnection.close()
    
    def device(self, serial) -> AdbDevice:
        return AdbDevice(self, serial)


    
