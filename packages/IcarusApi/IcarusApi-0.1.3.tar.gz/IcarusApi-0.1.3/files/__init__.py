class Excel:
    def get_names(self) -> list:
        """
        获取所有的表名\n
        :return:
        """
        ...

    def get_data(self, name: str) -> list:
        """
        获取表中数据\n
        :param name: 表名
        :return:
        """
        ...


def load_excel(file_path: str, no_column_name=False) -> Excel:
    """
    载入一个excel文件\n
    :param file_path: 文件路径
    :param no_column_name: 第一行不作为字段名，可省略，默认False
    :return:
    """
    ...


def save_excel(file_path: str, data: dict, columns: dict) -> Excel:
    """
    保存一个excel文件\n
    :param file_path: 文件路径
    :param data: {表名:[]{字段名:值}}
    :param columns: {表名:[]字段名}
    :return:
    """
    ...
