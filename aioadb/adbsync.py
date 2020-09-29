import asyncio
import datetime
import stat
import struct
from contextlib import asynccontextmanager
from collections import namedtuple
from functools import partial

from app.asyncdb.exceptions import PushSyncError, StartSyncError


FileInfo = namedtuple("FileInfo", ['mode', 'size', 'mtime', 'name'])


class Sync:
    def __init__(self, adbclient: 'AdbClient', serial: str) -> None:
        self._adbclient = adbclient
        self._serial = serial

    async def _prepare_sync(self, path: str, cmd: str) -> 'stream':
        stream = await self._adbclient._connect()
        try:
            await self._adbclient.adbconn.write(":".join(['host', 'transport', self._serial]))
            data = await stream.read_bytes(4)
            assert data == b'OKAY'
            await self._adbclient.adbconn.write("sync:")
            data = await stream.read_bytes(4)
            assert data == b'OKAY'
            await stream.write(
                cmd.encode("utf-8") + struct.pack("<I", len(path)) +
                path.encode("utf-8")
            )
            yield stream
        except Exception as e:
            raise StartSyncError(f'[*] not possible to start transfer file {e}')
        finally:
            stream.close()

    @asynccontextmanager 
    async def open_file(self, path: str, mode='rb') -> bytes:
        try:
            partial_open = partial(open, path, mode)
            # file = open(path, mode)
            loop = asyncio.get_event_loop()
            file = await loop.run_in_executor(None, partial_open)
            yield file
        except Exception as e:
            print(e)
        finally:
            file.close()
        
        
    async def stat(self, path: str) -> FileInfo:
        async with self._prepare_sync(path, "STAT") as stream:
            data = await stream.read_bytes(4)
            assert data == "STAT"
            mode, size, mtime = struct.unpack("<III", await stream.write.read_bytes(12))
            return FileInfo(mode, size, datetime.datetime.fromtimestamp(mtime), path)
    
    
    async def push(self, src, dst: str, mode: int = 0o755, filesize: int = None) -> None:
        # IFREG: File Regular
        # IFDIR: File Directory
        path = dst + "," + str(stat.S_IFREG | mode)
        total_size = 0
        async with self._prepare_sync(path, "SEND") as stream:
            # async with asyncio_extras.open_async(src, 'rb') as file:
            async with self.open_file(src) as file:
                try:    
                    loop = asyncio.get_event_loop()
                    while True:
                        # chunk = await file.read(4096)
                        chunk = await loop.run_in_executor(None, file.read, 4096)
                        if not chunk:
                            mtime = int(datetime.datetime.now().timestamp())
                            await stream.write(b"DONE" + struct.pack('<I', mtime))
                            break
                        await stream.write(b"DATA" + struct.pack("<I", len(chunk)))
                        await stream.write(chunk)
                        total_size += len(chunk)
                except Exception as e:
                    raise PushSyncError(f'[*] not possible to transfer a file to device {e}')


                