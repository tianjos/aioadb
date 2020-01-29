

class ShellMixin:

    async def _run(self, cmd: str) -> bytes:
        return await self.shell(cmd)
    
    async def app_start(self, package_name: str):
        await self._run(f'monkey -p {package_name} 1')

    async def list_third_packages(self):
        res = await self._run('pm list packages -3')
        return res
    
    async def resolution_screen(self):
        screen_size = await self._run(f'wm size')
        return screen_size
