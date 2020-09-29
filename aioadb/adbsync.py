import asyncio
import datetime
import stat
import struct
from contextlib import asynccontextmanager
from collections import namedtuple
from functools import partial

from .adbexceptions import PushSyncError, StartSyncError, OpenFileError


FileInfo = namedtuple("FileInfo", ['mode', 'size', 'mtime', 'name'])


class Sync:
    def __init__(self, adbclient: 'AdbClient', serial: str) -> None:
        self._adbclient = adbclient
        self._serial = serial

    @asynccontextmanager
    async def _prepare_sync(self, path: str, cmd: str) -> 'Stream':
        stream = await self._adbclient.get_stream()
        try:
            await stream.writer.write(":".join(['host', 'transport', self._serial]))
            data = await stream.reader.readexactly(4)
            assert data == b'OKAY'
            await stream.writer.write("sync:")
            data = await stream.reader.readexactly(4)
            assert data == b'OKAY'
            await stream.writer.write(
                cmd.encode("utf-8") + struct.pack("<I", len(path)) +
                path.encode("utf-8")
            )
            yield stream
        except Exception as e:
            raise StartSyncError(f'not possible to start transfer file {e}')
        finally:
            stream.writer.close()

    @asynccontextmanager 
    async def open_file(self, path: str, mode='rb') -> bytes:
        try:
            partial_open = partial(open, path, mode)
            loop = asyncio.get_event_loop()
            file = await loop.run_in_executor(None, partial_open)
            yield file
        except Exception as e:
            raise OpenFileError(f'not possible to open the file: {path}')
        finally:
            file.close()
        
        
    async def stat(self, path: str) -> FileInfo:
        async with self._prepare_sync(path, "STAT") as stream:
            data = await stream.reader.readexactly(4)
            assert data == "STAT"
            mode, size, mtime = struct.unpack("<III", await stream.reader.readexactly(12))
            return FileInfo(mode, size, datetime.datetime.fromtimestamp(mtime), path)
    
    
    async def push(self, src, dst: str, mode: int = 0o755, filesize: int = None) -> None:
        # IFREG: File Regular
        # IFDIR: File Directory
        path = dst + "," + str(stat.S_IFREG | mode)
        total_size = 0
        async with self._prepare_sync(path, "SEND") as stream:
            async with self.open_file(src) as file:
                try:    
                    loop = asyncio.get_event_loop()
                    while True:
                        chunk = await loop.run_in_executor(None, file.read, 4096)
                        if not chunk:
                            mtime = int(datetime.datetime.now().timestamp())
                            await stream.writer.write(b"DONE" + struct.pack('<I', mtime))
                            break
                        await stream.writer.write(b"DATA" + struct.pack("<I", len(chunk)))
                        await stream.writer.write(chunk)
                        total_size += len(chunk)
                except Exception as e:
                    raise PushSyncError(f'[*] not possible to transfer a file to device {e}')


                