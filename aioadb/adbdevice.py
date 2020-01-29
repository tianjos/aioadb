from .mixin import ShellMixin


class AdbDevice(ShellMixin):
    def __init__(self, adbclient: "AdbClient", serial: str):
        self._adbclient = adbclient
        self._serial = serial
        self._screen_size = None
        self._ip_address = None

    @property
    def serial(self):
        return self._serial
    
    @property
    def screen_size(self):
        return self._screen_size
    
    @screen_size.setter
    def screen_size(self, dimensions):
        self._screen_size = dimensions

    @property
    def ip_address(self):
        return self._ip_address
    
    @ip_address.setter
    def ip_address(self, addr):
        self._ip_address = addr
    
    def __repr__(self):
        return f"AdbDevice(serial={self.serial}"
    
    async def shell(self, cmd):
        output = await self._adbclient.shell(self._serial, cmd)
        return output 
