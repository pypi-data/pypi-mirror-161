RED = 0
YELLOW = 0
BLACK = 0
GREEN = 0
MAGENTA = 0
CYAN = 0
WHITE = 0  # 可用颜色


def echo(something, color=WHITE, end="\n") -> None:
    """
    建议使用的输出\n
    :param something: 可以为任意类型，如果是字典，列表将输出他们在go中的结构
    :param color: 输出的颜色，可省略，默认为白色
    :param end: 输出的结尾，可省略，默认为换行符
    :return:
    """
    ...


def select(title: str, items: list) -> (int, str):
    """
    生成一个选择菜单，方向键选择，Enter确认 \n
    :param title: 标题
    :param items: 可选择的项目，字符串列表，若为空则不会阻塞
    :return: 返回选项序号与选项文本
    """
    ...


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


def walkdir(path: str) -> list:
    """
    遍历文件夹\n
    :param path: 路径
    :return: 所有文件与文件夹
    """
    ...


def unzip(src: str, passwd: str, dest: str) -> None:
    """
    解压zip \n
    :param src: zip文件路径
    :param passwd: 密码，可省略，默认为空字符串
    :param dest: 目标路径，可省略，默认解压在zip同目录下
    :return:
    """
    ...


def notice(title: str, msg: str, png_path="", beep=False) -> bool:
    """
    弹出通知\n
    :param title: 标题
    :param msg: 消息
    :param png_path: 显示图片，可省略，默认为空字符串
    :param beep: 是否蜂鸣，可省略，默认false
    :return:
    """
    ...


def read_file(file_path: str) -> bytes:
    """
    读取文件\n
    :param file_path:
    :return:
    """
    ...


def save_file(file_path: str, content: str, cover=False) -> None:
    """
    保存文件\n
    :param file_path: 保存文件路径
    :param content: 内容
    :param cover: 是否覆盖，可省略，默认false
    :return:
    """
    ...


def input(prefix=">", color=WHITE, items={}) -> str:
    """
    带有补全提示的输入\n
    :param prefix: 前缀，可省略，默认为">"
    :param color: 颜色，前缀的颜色，可省略，默认为utils.WHITE
    :param items: 字典，键为提示词，值为描述。e.g.{"hello":"你好"}，可省略，默认空
    :return:
    """
    ...


def search(text: str, items: list, fuzzy=False) -> dict:
    """
    在字符串列表中搜索字符串\n
    :param text: 需要搜索的字符串
    :param items: 被搜索的字符串列表
    :param fuzzy: 是否启用模糊搜索，可省略，默认False
    :return: 返回一个字符串字典，值为搜索到的结果，键为结果所在行
    """
    ...


def exec_js(script: str) -> str:
    """
   执行JavaScript代码\n
   :param script: js代码
   :return:
   """
    ...


def exec_js_file(file_path: str) -> str:
    """
   执行js文件\n
   :param file_path: js文件路径
   :return:
   """
    ...


def format(format_str: str, *args) -> str:
    """
    格式化字符串\n
    :return:
    """


class ProgressBar:
    def __init__(self):
        ...

    def set(self):
        """
        设置进度\n
        :return:
        """
        ...

    def add(self):
        """
        增加进度\n
        :return:
        """
        ...
