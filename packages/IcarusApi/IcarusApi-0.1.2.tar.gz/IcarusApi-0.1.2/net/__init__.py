GET = "GET"
POST = "POST"


class Response:
    def status_code(self) -> int:
        """
        响应包状态码\n(如果为-1则表示请求过程发生错误，详细错误用text()方法查看。\n
        :return:
        """
        ...

    def headers(self) -> dict:
        """
        响应头\n
        存在多个值的响应头以列表储存。\n
        :return:
        """
        ...

    def text(self) -> str:
        """
        获取响应正文\n
        :return:
        """
        ...

    def content(self) -> bytes:
        """
        获取响应正文(bytes)\n
        :return:
        """
        ...


class Requester:
    def __init__(self, raw: str):
        """
        请求器可以通过规则生成请求，并按规则批量发送（尚不可用）\n
        :param raw: 基础请求包
        """
        ...

    def send(self, proxy_name: str, verify: bool) -> list:
        ...

    def set_proxy(self, name: str, proxy: dict) -> None:
        ...

    def set_verify(self, verify: bool):
        ...


def download(url: str, save_path: str, proxy_url: str) -> bool:
    """
    下载文件\n
    :param url: 文件url
    :param save_path: 文件保存路径，如果是文件将会写入文件。可省略，默认当前Icarus工作目录
    :param proxy_url: 代理url，可省略。e.g. http://127.0.0.1:7890 代理到本地clash
    :return: 下载是否成功
    """
    ...


def request(method: str, url: str, params: dict, data: str, headers: dict, verify: bool, proxy: dict) -> Response:
    """
    发送http请求\n
    :param method: GET,POST
    :param url: 目标url
    :param params: url参数，可省略
    :param data: post文本，可省略
    :param headers: 请求头,可省略
    :param verify: 是否验证https，可省略，默认为不验证
    :param proxy: 是否使用代理，可省略
    :return: Response
    """
    ...


def ssh(address: str, user: str, passwd_or_private_key_path: str) -> None:
    """
    启动一个交互式的shell\n
    :param address: 目标地址
    :param user: 用户名
    :param passwd_or_private_key_path: 密码或私钥文件路径
    :return:
    """
    ...


def ssh_run(address: str, user: str, passwd_or_private_key_path: str, command: str) -> None:
    """
    通过ssh执行命令并启动交互式\n
    :param address: 目标地址
    :param user: 用户名
    :param passwd_or_private_key_path: 密码或私钥文件路径
    :param command: 需要执行的命令
    :return:
    """
    ...


def ssh_exec(address: str, user: str, passwd_or_private_key_path: str, command: str) -> str:
    """
    通过ssh执行命令并立即断开连接\n
    :param address: 目标地址
    :param user: 用户名
    :param passwd_or_private_key_path: 密码或私钥文件路径
    :param command: 需要执行的命令
    :return: 返回命令执行输出
    """
    ...


class Tcp:
    def __init__(self, address: str):
        """
        建立tcp连接\n
        :param address: 地址
        """
        ...

    def send(self, data: str):
        """
        发送字符串\n
        :param data:
        :return:
        """
        ...

    def send_line(self, data: str):
        """
        发送字符串，但会在末尾加换行符\n
        :param data:
        :return:
        """
        ...

    def send_bytes(self, data: bytes):
        """
        发送字节数组\n
        :param data:
        :return:
        """
        ...

    def send_line_bytes(self, data: bytes):
        """
        发送字节数组，但会在末尾加换行符\n
        :param data:
        :return:
        """
        ...

    def recv(self) -> bytes:
        """
        接收所有数据\n
        :return: 返回字节数组
        """
        ...

    def recv_line(self) -> bytes:
        """
        接收数据到换行符停止\n
        :return: 返回字节数组
        """
        ...

    def interactive(self):
        """
        启用交互式收发数据\n
        :return:
        """
        ...

    def log(self):
        """
        显示收发日志\n
        :return:
        """
        ...
