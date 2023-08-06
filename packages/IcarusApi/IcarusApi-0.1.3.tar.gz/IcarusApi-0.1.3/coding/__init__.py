def bytes_to_string(b: bytes) -> str:
    """
    bytes转字符串\n
    :param b: 字节列表
    :return:
    """
    ...


def utf8(charset: str, text: str) -> str:
    """
    将其他字符集文本转换为utf8\n
    :param charset: 源文本使用的字符集
    :param text: 源文本
    :return:
    """
    ...


def json_loads(json_data: str) -> dict:
    """
    反序列化json对象\n
    :param json_data: 序列化的对象
    :return: 反序列化后的对象(dict或list)
    """
    ...


def json_dumps(obj: object) -> str:
    """
    序列化对象\n
    :param obj: 对象
    :return: 序列化后的对象
    """
    ...
