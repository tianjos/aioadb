import abc
import inspect
import sys
import traceback
from functools import wraps


def pre_parser(func):
    @wraps(func)
    async def wrapper_parser(*args, **kwargs):
        *rest, arg = args
        parser_cls = ParserFactory.parsers.get(_lookup_func_name(func), DefaultParser)
        pre_parse = parser_cls.parse(arg)
        output = await func(*rest, pre_parse, **kwargs)
        return output
    return wrapper_parser

def pos_parser(func):
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


class PackagesParser(AbstractParser):

    @classmethod
    def parse(cls, output: bytes) -> list:
        try:
            return list(map(lambda pkg: pkg.split(":")[1], output.decode().split()))
        except AttributeError:
            stack = inspect.stack()
            for frame in stack:
                if frame.function == 'wrapper_parser':
                    args = inspect.getargvalues(frame.frame)
                    kw = args.locals.get('kwargs').values()
        return f'No packages matching the criteria: {" ".join(*kw)}'


class WriteTextParser(AbstractParser):

    @classmethod
    def parse(cls, text: str) -> str:
        escaped_text = text.translate(str.maketrans({"-":  r"\-",
                                                "+":  r"\+",
                                                "[":  r"\[",
                                                "]":  r"\]",
                                                "(":  r"\(",
                                                ")":  r"\)",
                                                "{":  r"\{",
                                                "}":  r"\}",
                                                "\\": r"\\\\",
                                                "^":  r"\^",
                                                "$":  r"\$",
                                                "*":  r"\*",
                                                ".":  r"\.",
                                                ",":  r"\,",
                                                ":":  r"\:",
                                                "~":  r"\~",
                                                ";":  r"\;",
                                                ">":  r"\>",
                                                "<":  r"\<",
                                                "%":  r"\%",
                                                "#":  r"\#",
                                                "\'":  r"\\'",
                                                "\"":  r'\\"',
                                                "`":  r"\`",
                                                "!":  r"\!",
                                                "?":  r"\?",
                                                "|":  r"\|",
                                                "=":  r"\=",
                                                "@":  r"\@",
                                                "/":  r"\/",
                                                "_":  r"\_",
                                                " ":  r"%s", # special
                                                "&":  r"\&"}))
        return escaped_text


class WlanIpParser:

    @classmethod
    def parse(cls, output: bytes) -> str:
        return output.decode().split()[-1]
        

class ParserFactory:
    parsers = {
        #pos-parsers
        'ResolutionScreen': ResolutionScreenParser,
        'Packages': PackagesParser,
        'WlanIp': WlanIpParser,
        #pre-parsers
        'WriteText': WriteTextParser,
        }

        