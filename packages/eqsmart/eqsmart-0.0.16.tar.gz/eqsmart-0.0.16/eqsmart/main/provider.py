import json
import socket
import sys
from threading import Thread
from eqsmart.components.protocol import *
import traceback


def not_c_key(p_dict, p_key):
    """
    判断不包含元素
    :param p_dict: 字典
    :param p_key: key
    :return: p_dict 不包含 p_key, 返回 True
    """
    try:
        if p_dict.__contains__(p_key) is True and p_dict[p_key] is not None and p_dict[p_key] != '':
            return False
    except Exception as e:
        print('[eqsmart]', 'conf check', str(e))
    return True


class Provider:
    def __init__(self, provider_conf, server_info, server_list):
        self.provider_conf = {}
        self.server_info = server_info
        self.server_list = server_list
        self.provider_conf['HOST'] = '127.0.0.1' if not_c_key(provider_conf, 'HOST') else provider_conf['HOST']
        self.provider_conf['PORT'] = 7901 if not_c_key(provider_conf, 'PORT') else provider_conf['PORT']
        self.provider_conf['BACKLOG'] = 5 if not_c_key(provider_conf, 'BACKLOG') else provider_conf['BACKLOG']
        self.provider_conf['BUF_SIZE'] = 1024 if not_c_key(provider_conf, 'BUF_SIZE') else provider_conf['BUF_SIZE']
        self.provider_conf['IP'] = '127.0.0.1' if not_c_key(provider_conf, 'IP') else provider_conf['IP']
        self.provider_conf['WEIGHT'] = 1 if not_c_key(provider_conf, 'IP') else provider_conf['WEIGHT']

    def __send_data__(self):
        register_data = []
        send_data = {
            'type': 'provider register',
            'remote': {
                'ip': self.provider_conf['IP'],
                'port': self.provider_conf['PORT'],
                'weight': self.provider_conf['WEIGHT']
            },
            'service_name': '',
            'func': []
        }
        for item in self.server_info:
            send_data['service_name'] = item
            send_data['func'] = self.server_info[item]
            register_data.append(send_data.copy())
        return register_data

    def __func_call__(self, connect):
        while True:
            '''处理客户端端数据'''
            try:
                """
                recv(buffer_size) 接收TCP数据，数据以字符串形式返回，buffer_size 指定要接收的最大数据量
                """
                data = connect.recv(self.provider_conf['BUF_SIZE'])
                data = str(data, 'UTF-8')
                if data == '':
                    break
                data_json = json.loads(data)
                print('[eqsmart] [provider] 接收到客户端数据:', data_json)
                response = protocol_analysis(data_json)
                try:
                    call_func = self.server_list.copy()
                    for item in data_json['service_name']:
                        call_func = call_func[item]
                    method = getattr(call_func['func'], data_json['func'])
                    response = method(*tuple(data_json['args']), **data_json['kwargs'])
                except Exception as e:
                    print(e, traceback.format_exc())
                    response['code'] = 'remote_func_call_error'
                    response['message'] = str(e) + str(traceback.format_exc())
                print('[eqsmart] [provider] 返回给客户端数据:', response)
                connect.sendall(bytes(json.dumps(response).encode('utf-8')))
            except socket.error as e:
                print(str(e))
                break
        '''关闭客户端连接'''
        connect.close()

    def server_init(self, register):
        """
        服务端 socket 初始化
        :return: None
        """

        try:
            """
            创建套接字：socket.socket([family[, type[, proto]]])
            family: 套接字家族可以使 AF_UNIX 或者 AF_INET
            type: 套接字类型可以根据是面向连接的还是非连接分为 SOCK_STREAM 或 SOCK_DGRAM
            protocol: 一般不填默认为 0
            """
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            print('[eqsmart] [Provider] [初始化异常] ' + str(e))
            sys.exit()

        try:
            """
            bind() 绑定地址(host,port)到套接字， 在AF_INET下，以元组(host,port)的形式表示地址
            """
            server.bind((self.provider_conf['HOST'], self.provider_conf['PORT']))
            print('[eqsmart] [Provider Starting] ' + self.provider_conf['HOST'] + ':' + str(self.provider_conf['PORT']))
        except socket.error as e:
            print("[eqsmart] Bind failed!" + str(e))
            sys.exit()
        print("[eqsmart] Provider bind complete")

        ''' 启动一个线程，将自身注册到注册中心 '''
        send_data = self.__send_data__()
        for i in send_data:
            Thread(target=register, args=(i,)).start()
        """
        listen(backlog) 开始TCP监听。backlog指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5即可
        """
        server.listen(self.provider_conf['BACKLOG'])
        print("[eqsmart] Provider now listening")

        while True:
            """
            accept() 被动接受TCP客户端连接,(阻塞式)等待连接的到来
            """
            connect, addr = server.accept()
            print("[eqsmart] Provider connected with %s:%s " % (addr[0], str(addr[1])))
            """
            启动线程
            """
            Thread(target=self.__func_call__, args=(connect,)).start()
