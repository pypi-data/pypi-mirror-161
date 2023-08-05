"""
yaml 配置文件读取
"""
import yaml


class ReadConf:
    def __init__(self, path):
        """
        配置文件读取类初始化
        :param path: 配置文件路径
        """
        self.conf_path = path
        self.configuration = {}

    def __read__(self, item):
        """
        读取配置项
        :param item: 要读取的配置项 如：a.b.c
        :return:
        """
        if bool(self.configuration) is False:
            ''' 相同的yaml文件读取一次即可 '''
            try:
                f = open(self.conf_path, 'r', encoding='utf-8')
                cont = f.read()
                self.configuration = yaml.load(cont, Loader=yaml.FullLoader)
            except Exception as e:
                print(e)
                return ''
        ''' 解析要读取的配置项结果 '''
        items = item.split('.')
        res = self.configuration
        for i in items:
            res = res[i]
        return res

    def __file_load__(self):
        """
        加载配置文件内容到 self.configuration
        :return: void
        """
        if bool(self.configuration) is False:
            try:
                f = open(self.conf_path, 'r', encoding='utf-8')
                cont = f.read()
                self.configuration = yaml.load(cont, Loader=yaml.FullLoader)
            except Exception as e:
                print(e)
