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


def json_indent(json_data: str) -> str:
    """
    通过添加缩进美化json格式\n
    :param json_data: 序列化的对象
    :return:
    """


def url_decode(url: str) -> str:
    """
    url解码\n
    :param url: 需要解码的文本
    :return:
    """
    ...


def url_encode(text: str) -> str:
    """
    url编码\n
    :param text: 需要编码的文本
    :return:
    """
    ...
