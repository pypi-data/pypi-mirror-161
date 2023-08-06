BASH = 0
TELNET = 1


def PUT_PUBLIC_KEY(key_or_key_path: str) -> str:
    """
    生成添加公钥命令\n
    :params key_or_key_path: 公钥字符串或公钥文件路径
    :return:
    """
    ...


def REVERSE_SHELL(address: str, mode: int) -> str:
    """
    生成反弹shell命令\n
    :param address: 接收shell的地址
    :param mode: payload模式，可省略，默认为cmds.BASH
    :return:
    """
    ...


def NC_LISTEN(port: int) -> str:
    """
    生成nc监听命令（tcp）\n
    :param port: 监听端口
    :return:
    """
    ...
