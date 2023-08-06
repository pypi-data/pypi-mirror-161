def match(left: str, right: str, text: str) -> list:
    """
    匹配文本中满足条件的全部文本（正则实现）\n
    e.g.
    \t echo(match("a", "c", "abc aqc")) \n
    \t result: ["b","q"] \n
    :param left: 左侧文本
    :param right: 右侧文本
    :param text: 需要匹配的文本
    :return: 返回包含结果的字符串列表
    """
    ...


def replace(text: str, old: str, new: str, num=-1) -> list:
    """
    字符串替换\n
    :param text: 文本
    :param old: 原始字符串
    :param new: 替换字符串
    :param num: 替换次数，可省略，默认-1为全部替换
    :return:
    """
    ...
