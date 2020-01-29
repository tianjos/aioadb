## Description:
### This is a basic project based on adbutils project API and asyncio API.
-----------------------------------------

## Example:
* Listing third packages
```import asyncio

from aioadb.adbclient import AdbClient
from aioadb.adbdevice import AdbDevice


async def main():
    adbclient = AdbClient("adb_host", adb_port)
    await adbclient.connect_to_adb()
    device = adbclient.device("serial")
    packages = await device.list_third_packages()
    print(packages)
    
if __name__ == "__main__":
    asyncio.run(main())
```
