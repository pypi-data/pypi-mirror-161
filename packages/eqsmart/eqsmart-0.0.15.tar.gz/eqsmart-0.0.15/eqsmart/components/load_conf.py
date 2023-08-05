"""
配置文件的读取
"""
from eqsmart.components.read_conf import ReadConf


class LoadConf:
    def __init__(self, path, start_params):
        """
        初始化
        :param path: 配置文件路径
        :param start_params: 应用启动参数
        """
        self.configuration_ext = {}
        self.configuration = ReadConf(path)
        self.configuration.__file_load__()
        if 'env' in start_params:
            ''' 启动参数传入运行环境信息时，额外加载环境配置文件 '''
            self.load_ext(path[:-5] + '-' + start_params['env'] + path[-5:])
        else:
            ''' 启动参数未传入运行环境信息，判断主配置文件是否指定环境信息 '''
            if 'env' in self.configuration.configuration['app']:
                self.load_ext(path[:-5] + '-' + self.configuration.configuration['app']['env'] + path[-5:])
        if 'port' in start_params:
            ''' 支持启动参数强制指定端口 '''
            self.configuration.configuration['app']['link_server']['port'] = int(start_params['port'])

    def node_read(self, conf_node):
        """
        读取服务启动配置信息
        :return: 配置信息节点
        """
        res = None
        try:
            res = self.configuration.__read__(conf_node)
        except Exception as e:
            print('[eqsmart] [read conf]', conf_node, 'not exist', str(e))
        return res

    def load_ext(self, path):
        """
        加载附加环境配置文件信息
        :param path: 附加环境路径
        :return: void
        """
        self.configuration_ext = ReadConf(path)
        self.configuration_ext.__file_load__()
        self.configuration.configuration.update(self.configuration_ext.configuration)


def get_run_params(input_params):
    """
    启动参数处理
    :param input_params: 应用启动参数 ['env=dev', 'port=7877']
    :return: 启动参数格式化 {'env':'dev', 'port':'7877'}
    """
    run_params = {}
    for item in input_params:
        try:
            info = item.split('=')
            run_params[info[0]] = info[1]
        except Exception as e:
            print('仅解析 a=b 格式的启动参数，其他跳过，', e)
    return run_params
