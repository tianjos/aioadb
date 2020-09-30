import enum


class ADBEnum(bytes, enum.Enum):
    OKAY = b'OKAY'
    SUCCESS = b'Success'
    STAT = b'STAT'
    DONE = b'DONE'
    DATA = b'DATA'
    SEND = b'SEND'