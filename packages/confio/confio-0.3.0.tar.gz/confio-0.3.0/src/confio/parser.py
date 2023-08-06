from enum import Enum
from logging import getLogger

logger = getLogger('confio')


class ConfTypes(Enum):
    """
    配置项的类型
    """

    NONE = ''
    """
    无类型
    """

    EXPR = 'expr'
    """
    表达式
    """

    PATH = 'path'
    """
    路径
    """

    SIZE = 'size'
    """
    文件大小
    """

    TIME = 'time'
    """
    时间值
    """


SIZE = {
    'b': 1,
    'k': 1024,
    'm': 1024 ** 2,
    'g': 1024 ** 3,
    't': 1024 ** 4,
    'p': 1024 ** 5
}

TIME = {
    's': 1,
    'm': 60,
    'h': 60 ** 2,
    'D': 60 ** 2 * 24,
    'M': 60 ** 2 * 24 * 30,
    'Y': 60 ** 2 * 24 * 365,
}


class ValueParser:
    PATH_ROOT = None
    INTERCEPTORS = []
    enum_class_ext = None
    """
    扩展枚举类型
    """

    def __init__(self, path_root: str = None):
        self.path_root = path_root or self.PATH_ROOT

    def cast_enum(self, enum_value):
        """
        将 enum_class 的值转换成 enum_class 对象
        """
        if self.enum_class_ext:
            try:
                return self.enum_class_ext(enum_value)
            except Exception:
                pass
        try:
            return ConfTypes(enum_value)
        except Exception:
            if self.enum_class_ext:
                logger.error('Cannot cast value %r into type "%s" or type "ConfTypes"' % (
                    enum_value, self.enum_class_ext.__name__
                ))
            else:
                logger.error('Cannot cast value %r into type "ConfTypes"' % enum_value)
            return ConfTypes.NONE

    def parse_path(self, value):
        import os
        if not os.path.isabs(value):
            if self.path_root is None:
                raise Exception(
                    'The path root must be specified via `ValueParser.PATH_ROOT=` or `ValueParser(path_root=)`'
                )
            value = os.path.join(self.path_root, value)
        return os.path.abspath(value)

    @classmethod
    def call_interceptors(cls, parse_type: ConfTypes, raw_value, parsed_value, prev_value):
        for interceptor in cls.INTERCEPTORS:
            prev_value = interceptor(parse_type, raw_value, parsed_value, prev_value)
        return prev_value

    @classmethod
    def add_interceptor(cls, interceptor):
        cls.INTERCEPTORS.append(interceptor)

    @classmethod
    def parse_expr(cls, value):
        return eval(value)

    @classmethod
    def parse_size(cls, value):
        if isinstance(value, int):
            return value
        temp = []
        for ch in value:
            if not ch.isalpha():
                temp.append(ch)
                continue
            temp.append('*%s+' % SIZE[ch.lower()])
        # 最后的右边可能存在一个多余的 + 符号
        expr = ''.join(temp).rstrip('+')
        return eval(expr)

    @classmethod
    def parse_time(cls, value):
        if isinstance(value, int):
            return value

        temp = []
        for ch in value:
            if not ch.isalpha():
                temp.append(ch)
                continue
            temp.append('*%s+' % TIME[ch])
        # 最后的右边可能存在一个多余的 + 符号
        expr = ''.join(temp).rstrip('+')
        return eval(expr)
