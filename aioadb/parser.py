import abc
from functools import wraps


def parser(func):
    @wraps(func)
    async def wrapper_parser(*args, **kwargs):
        parser_cls = ParserFactory.parsers.get(_lookup_func_name(func), DefaultParser)
        output = await func(*args, **kwargs)
        return parser_cls.parse(output)
    return wrapper_parser

def _lookup_func_name(func):
    return ''.join(list(map(str.capitalize, func.__name__.split('_'))))


class AbstractParser(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def parse(cls, output: bytes) -> str:
        pass
    

class DefaultParser(AbstractParser):

    @classmethod
    def parser(cls, output: bytes) -> str:
        return output.decode()


class ResolutionScreenParser(AbstractParser):

    @classmethod
    def parse(cls, output: bytes) -> list:
        return list(map(int, output.decode().split(':')[1].strip().split('x')))


class ListThirdPackagesParser(AbstractParser):

    @classmethod
    def parse(cls, output: bytes) -> list:
        return list(map(lambda pkg: pkg.split(":")[1], output.decode().split()))
        

class ParserFactory:
    parsers = {
        'ResolutionScreen': ResolutionScreenParser,
        'ListThirdPackages': ListThirdPackagesParser,
        }

        