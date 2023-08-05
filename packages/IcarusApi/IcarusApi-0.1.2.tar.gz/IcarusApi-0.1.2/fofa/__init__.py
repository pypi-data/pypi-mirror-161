class Fofa:
    def __init__(self, email: str, key: str):
        """
        连接FOFA\n
        :param email: 邮箱
        :param key: 密钥
        """
        ...

    def info(self) -> dict:
        """
        获取账号信息\n
        :return: 字符串字典
        """

    def search(self, query: str, page: int) -> list:
        """
        向FOFA提交搜索请求\n
        :param query: 查询语句
        :param page: 页码
        :return: 返回结果列表
        """
        ...
