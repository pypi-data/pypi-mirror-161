import re
from typing import Any
from datetime import datetime


# 检测ip是否正确
def check_is_ip(ip: str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    return False


def check_is_digital(value: str) -> bool:
    result = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$').match(str(value))
    if result:
        return True
    else:
        return False


# 格式化数字字母以外的字符 \u4e00-\u9fa5_
def format_name(name: str, pattern: str = r'[^a-zA-Z0-9_]+', replace: str = '_'):
    if name is None:
        return ''
    else:
        return re.sub(r'^_|_$', '', re.sub(pattern, replace, name.strip()))


def format_value(value: Any, mapping: dict = {}, decimal: int = 3):
    if isinstance(value, str):
        return format_value(mapping.get(value, value), mapping, decimal)
    elif isinstance(value, float):
        value = f"{value: .{decimal}f}"
        return f"{float(value): g}"
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, bool):
        return 1 if value else 0
    elif isinstance(value, int):
        return value
    return str(value)


# 匹配搜索
# \w{3}:.*?;;\n   reg:testdtu;;\n
#  QQ交流群:(?P<QQ>\d+) blog地址:(?P<blog>.*?) 欢迎收藏
def search_match(value: str, pattern: str = r'(?P<xxx>.*?)') -> dict:
    return re.search(pattern, value).groupdict()