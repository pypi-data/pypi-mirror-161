from http.server import HTTPServer, BaseHTTPRequestHandler
from socket import gethostbyname, gethostname
import json
from eqsmart.main.provider import not_c_key


def preset_get_params(request):
    """
    GET 参数列表格式化
    :param request: GET请求链接
    :return: service_path 服务地址, params 参数列表
    """
    service_path = []
    params = {}
    try:
        path_params = request.split('?')
        service_path = path_params[0][1:].split('/')
        params_item = path_params[1].split('&')
        for item in params_item:
            key_value = item.split('=')
            params[key_value[0]] = key_value[1]
    except Exception as e:
        print('[eqsmart] [GET 参数读取失败]', e)
    return service_path, params


def func_exec(service_list, service_path, params):
    """
    函数执行
    :param service_list: 服务列表
    :param service_path: 服务方法的路径
    :param params: 服务方法入参
    :return: 执行结果
    """
    print(service_list)
    try:
        for i in service_path[:-1]:
            service_list = service_list[i]
        method = getattr(service_list['func'], service_path[-1])
        response = method(**params)
    except Exception as e:
        print('[eqsmart] [函数执行失败]', e)
        response = 'Function execution failed! Details: ' + str(e)
    return response


class MyHttpServer(BaseHTTPRequestHandler):
    my_server_list = {}
    server_version = "Apache"
    sys_version = 'Python/3'

    def do_GET(self):
        """
        处理GET请求
        :return: http response
        """
        path = self.path
        service_path, params = preset_get_params(path)
        res = func_exec(self.my_server_list, service_path, params)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("test1", "This is test!")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())

    def do_POST(self):
        """
        处理POST请求
        :return: http response
        """
        path = self.path
        data = self.rfile.read(int(self.headers['content-length']))
        data = json.loads(data)
        service_path = path[1:].split('/')
        res = func_exec(self.my_server_list, service_path, data)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("test", "This is post!")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode())


def http_server(server_conf, server_list):
    """
    实例化http服务器对象
    :param server_conf: http服务器配置
    :param server_list: http服务列表
    :return: http服务器对象
    """
    host = gethostbyname(gethostname()) if not_c_key(server_conf, 'HOST') else server_conf['HOST']
    mhs = MyHttpServer
    mhs.my_server_list = server_list
    print(f"[eqsmart] HTTP Server starting on {host}:{server_conf['PORT']}")
    server = HTTPServer((host, server_conf['PORT']), mhs)
    return server


def main():
    hs = http_server({'PORT': 9701}, {'user_service': TestCommon()})
    hs.serve_forever()


class TestCommon:
    name = 'eqsmart'
    age = '1'

    def add_user(self, name, age):
        self.name = name
        self.age = age
        return 'hello' + name


if __name__ == '__main__':
    main()
