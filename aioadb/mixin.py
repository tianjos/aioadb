from .parser import pre_parser, pos_parser


class ShellMixin:

    async def _run(self, cmd: str) -> bytes:
        return await self.shell(cmd)
    
    async def app_start(self, package_name: str) -> None:
        await self._run(f'monkey -p {package_name} 1')
    
    @pos_parser
    async def packages(self, flags: list = None) -> list:
        if flags is None: flags = []
        return await self._run(f'pm list packages {" ".join(flags)}')
    
    @pos_parser
    async def resolution_screen(self) -> list:
        return await self._run('wm size')
    
    async def swipe(self, sx, sy, ex, ey: str, duration: int = 400) -> None:
        await self._run(f'input swipe {sx} {sy} {ex} {ey} {str(duration)}')

    async def touch(self, x, y: str) -> None:
        await self._run(f'input tap {x} {y}')
    
    @pre_parser
    async def write_text(self, text: str) -> None:
        await self._run(f'input text {text}')
    
    async def key_event(self, key_code: int) -> None:
        await self._run(f'input keyevent {str(key_code)}')
    
    @pos_parser
    async def wlan_ip(self) -> None:
        return await self._run(f'ip route')
