def argv(name: int) -> str:
    """
    获取Icarus命令行参数\n
    :param name: 可以是整型也可以是字符串
    :return: 值
    """
    ...


def env(name: str, value: str) -> str:
    """
    获取Icarus环境变量\n
    :param name: 变量名
    :param value: 若此参数不存在则为获取，若此参数存在则为修改
    :return: 环境变量的值
    """
    ...


def shell_exec(cmd: str, args: list, visible: bool, cmd_dir: str) -> int:
    """
    在本地执行shell命令，以任务执行，非阻塞函数。\n
    ps.记得使用kill_task()终止\n
    :param cmd: 要执行的命令
    :param args: 命令行参数，类型为字符串列表，可省略
    :param visible: 执行结果是否可见，可省略，默认为可True
    :param cmd_dir: 执行命令的位置，可省略
    :return: 返回任务id
    """


def shell_fetch(tid: int, all_data: bool) -> (str, str):
    """
    获取shell执行的结果，返回标准输出与标准错误。\n
    :param tid: 任务序号
    :param all_data: 是否取回完整内容，可省略，默认为false
    :return: 两个字符串(标准输出,标准错误)
    """
    ...


def kill_task(tid: int) -> None:
    """
    终止任务。\n
    :param tid: 任务序号
    :return:
    """
    ...


def version() -> str:
    """
    获取ICARUS版本\n
    :return:
    """
    ...


def platform() -> str:
    """
    获取操作系统类型\n
    :return:
    """
    ...
