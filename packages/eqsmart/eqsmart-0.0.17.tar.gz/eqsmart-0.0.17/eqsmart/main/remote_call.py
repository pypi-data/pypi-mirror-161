import math
import random

from eqsmart.main.consumer import Consumer
from eqlink.components.remote_server import remote_server
from eqlink.main.clent import fail_server_list
import json

protocol = {
    'type': 'call provider',
    'service_name': '',
    'func': '',
    'args': (),
    'kwargs': {}
}


class RemoteCall:
    def __init__(self, service_path):
        self.service_path = service_path

    def func_call(self, params, buf_size=204800):
        if type(params) is tuple:
            protocol['args'] = params
            protocol['kwargs'] = {}
        else:
            protocol['kwargs'] = params
            protocol['args'] = ()
        service_path = self.service_path.split('/')
        protocol['service_name'] = service_path[:-1]
        protocol['func'] = service_path[-1]
        ''' 远程服务列表 '''
        provider_service_list = remote_server.__get__()
        ''' 远程服务地址信息'''
        provider_server = provider_service_list[service_path[0]]['remote']
        ''' 远程服务加权调用：计算权重 '''
        weight_check = {'0': 1}
        count_w = 0  # 用于远程服务遍历的计数器
        count_c = 0  # 权值和
        for item in provider_server:
            weight_check[str(count_w)] = item['weight']
            count_w = count_w + 1
            count_c = int(item['weight']) + count_c
        if count_c == 0:
            res_error = {
                'code': 'remote_call_error',
                'message': '远程服务权重计算失败，服务可能不存在',
                'data': protocol
            }
            return res_error
        weight_factor = math.ceil(100 / count_c)  # 权重因子
        weight_m = 0  # 中间值
        call_random = random.randint(0, 100)  # 随机数
        call_weight = 0  # 加权计算后，被调用的远程服务
        print('[eqsmart] 远程服务加权调用，服务权重:', weight_check)
        for item in weight_check.keys():
            c_weight = int(weight_check[item]) * weight_factor
            weight_check[item] = [weight_m, weight_m + c_weight]
            if weight_m <= call_random <= weight_m + c_weight:
                call_weight = int(item)
            weight_m = weight_m + c_weight
        print('[eqsmart] [加权调用]', call_weight, call_random)
        ''' 以上为加权调用的权重计算 '''
        provider_conf = {
            'IP': provider_server[call_weight]['ip'],  # 远程服务器地址
            'PORT': provider_server[call_weight]['port'],  # 远程服务器端口
            'BUF_SIZE': buf_size  # 消息读取长度
        }
        print('[eqsmart] 远程调用', provider_conf, protocol)
        try:
            remote_call = Consumer(provider_conf).func_call_int(protocol)
        except Exception as e:
            print('[eqsmart] 远程调用失败！', e)
            remote_call = json.dumps({'code': 'remote_call_error', 'message': str(e)})
        ''' 调用结果判断 '''
        res = json.loads(remote_call)
        try:
            if res['code'] == 'remote_call_error':  # remote_call_error --> 结果加入服务移除列表
                fail_server_list.append({'IP': provider_conf['IP'], 'PORT': provider_conf['PORT']})
        except Exception as e:
            ''' 远程调用可能不返回 code '''
            print('远程调用成功！', e)
        return res
