from .adbconnection import AdbConnection, Stream
from .adbdevice import AdbDevice
from .adbenum import ADBEnum
from .adbexceptions import AdbShellReadError, AdbConnectionClosedError
from .adbsync import Sync

class AdbClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._adbconnection = AdbConnection(self._host, self._port)
    
    async def connect_to_adb(self):
        await self._adbconnection.connect()
    
    async def get_stream(self) -> Stream:
        await self.connect_to_adb()
        return self._adbconnection.stream
    
    async def shell(self, serial: str, cmd: str):
        stream = await self.get_stream()
        await stream.write(f'host:transport:{serial}')
        await stream.check_adb_response(ADBEnum.OKAY)
        await stream.write(f'shell: {cmd}')
        await stream.check_adb_response(ADBEnum.OKAY)
        try:
            data = await stream.read_until_close()
            return data
        except Exception as e:
            raise AdbShellReadError(f"couldn't get all data from adb: {str(e)}")
        finally:
            await stream.close()

    async def server_version(self):
        stream = await self.get_stream()
        await stream.write('host:version')
        await stream.check_adb_response(ADBEnum.OKAY)
        data = stream.read_bytes(4)
        if not data:
            raise AdbConnectionClosedError('connection closed')
        size = int(data, 16)
        return await stream.read_bytes(size)

    def device(self, serial) -> AdbDevice:
        return AdbDevice(self, serial)
    
    def sync(self, serial) -> Sync:
        return Sync(self, serial)


    
