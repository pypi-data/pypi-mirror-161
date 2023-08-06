class Container:
    def __init__(self):
        ...

    def image(self) -> str:
        """
        生成此容器的镜像\n
        :return:
        """
        ...

    def status(self) -> str:
        """
        容器状态 (容器已启动/停止/重启的时长)\n
        :return:
        """
        ...

    def state(self) -> str:
        """
        容器阶段 (created,running,restarting,removing,paused,exited,dead)\n
        :return:
        """
        ...

    def id(self) -> str:
        """
        容器完整id (短id为前12位)\n
        :return:
        """
        ...

    def port(self) -> dict:
        """
        所有端口映射信息\n
        :return:
        """
        ...


class Docker:
    """
    连接docker daemon
    """

    def __init__(self):
        ...

    def images(self) -> list:
        """
        获取已下载的镜像 \n
        :return: 返回包含镜像名的字符串列表
        """
        ...

    def containers(self) -> list:
        """
        获取所有容器 \n
        :return: 返回容器列表
        """
        return [Container]

    def start_container(self, cid: str) -> bool:
        """
        启动容器 \n
        :return: 返回是否执行成功
        """
        ...

    def stop_container(self, cid: str) -> bool:
        """
        停止容器 \n
        :return: 返回是否执行成功
        """
        ...

    def remove_container(self, cid: str) -> bool:
        """
        移除容器 \n
        :return: 返回是否执行成功
        """
        ...

    def exec(self, cid: str, cmd: str) -> bool:
        """
        在容器中执行命令 \n
        :return: 返回执行是否成功
        """
        ...
