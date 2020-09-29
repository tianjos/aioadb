class BaseException(Exception):
    '''Base exception class'''
    pass


class SyncError(BaseException):
    '''Base sync exception class'''
    pass


class StartSyncError(SyncError):
    '''Raised when couldn't start sync'''
    pass


class PushSyncError(SyncError):
    '''Raised when couldn't complete push sync'''
    pass