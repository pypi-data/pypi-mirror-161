class Vault:
    def __init__(self, identifications: list):
        """
        用于搜索和聚合数据\n
        :param identifications: 身份识别字段
        """
        ...

    def exact_search(self, conditions: dict) -> list:
        """
        精确搜索\n
        :param conditions: 指定对应字段的搜索内容
        :return:
        """
        ...

    def fuzzy_search(self, conditions: dict) -> list:
        """
        模糊搜索\n
        :param conditions: 指定对应字段的搜索内容
        :return:
        """
        ...

    def search(self, query: str) -> list:
        """
        直接搜索\n
        :param query: 要搜索的字符串
        :return:
        """
        ...

    def load_json(self, name: str, json_data: str, columns_map: dict) -> None:
        """
        载入json数据库\n
        :param name: 数据库名
        :param json_data: json数据
        :param columns_map: json字段与vault字段对应表
        :return:
        """
        ...
