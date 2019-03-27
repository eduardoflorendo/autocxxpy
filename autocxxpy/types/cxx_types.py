# encoding: utf-8
import functools
import re

from autocxxpy.types.parser_types import Function, Variable

CXX_BASIC_TYPES = {
    "char8_t",
    "char16_t",
    "char32_t",
    "wchar_t",
    "char",
    "short",
    "int",
    "long",
    "long long" "unsigned char",
    "unsigned short",
    "unsigned int",
    "unsigned long",
    "unsigned long long",
    "float",
    "double",
}

_REMOVE_POINTER_RE = re.compile("[ \t]*\\*[ \t]*")
_FUNCTION_POINTER_RE = re.compile("(\\w+) +\\((\\w*)\\*(\\w*)\\)\\((.*)\\)")


@functools.lru_cache()
def is_const_type(t: str):
    if is_pointer_type(t):
        return t.endswith("const")
    return t.startswith('const ')


@functools.lru_cache()
def is_array_type(t: str):
    return t.endswith(']')


@functools.lru_cache()
def is_normal_pointer(t: str):
    """
    check if t is a T *
    """
    return remove_cvref(t).endswith('*')


@functools.lru_cache()
def is_pointer_type(t: str):
    """
    :param t:
    :return:
    :note function_type is also pointer type
    :sa is_function_type
    """
    return "*" in t


@functools.lru_cache()
def is_reference_type(t: str):
    return "&" in t


@functools.lru_cache()
def is_function_pointer_type(t: str):
    # int32 (__cdecl*name)(OesApiSessionInfoT *, SMsgHeadT *, void *, OesQryCursorT *, void *)
    return _FUNCTION_POINTER_RE.match(t)


@functools.lru_cache()
def pointer_base(t: str):
    t = remove_cvref(t)
    return t[:-2]


@functools.lru_cache()
def array_base(t: str):
    """
    :raise ValueError if t is not a array type
    """
    t = t[: t.rindex("[")]
    while t.endswith(' '):
        t = t[:-1]
    return t


@functools.lru_cache()
def array_count_str(t: str):
    t = t[t.rindex("[")+1:]
    t = t[:-1]
    return t


@functools.lru_cache()
def array_count(t: str):
    """
    :return: array_count, 0 if no count in this type.
    """
    t = array_count_str(t)
    if t:
        return int(t)
    return 0


@functools.lru_cache()
def strip(s: str):
    while s.startswith(' '):
        s = s[1:]
    while s.endswith(' '):
        s = s[:-1]
    return s


@functools.lru_cache()
def function_pointer_type_info(t: str) -> Function:
    m = _FUNCTION_POINTER_RE.match(t)
    if m:
        ret_type = m.group(1)
        calling_convention = m.group(2)
        args_str = m.group(4)

        func = Function(
            name=m.group(3),
            ret_type=ret_type,
            calling_convention=calling_convention if calling_convention else None
        )
        func.args = [
            Variable(name='', type=strip(arg), parent=func)
            for arg in args_str.split(',')
        ]
        return func


@functools.lru_cache()
def remove_cvref(t: str):
    if t.endswith(" const"):
        t = t[:-6]
    return (
        t.replace("const ", "")
            .replace("volatile ", "")
            .replace("&", "")
            .strip()
    )