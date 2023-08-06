"""
公共工具
"""


def protocol_analysis(protocol):
    """
    对协议类型进行分析和处理
    :param protocol: 协议 JSON 内容
    :return: void
    """
    if protocol['type'] == 'provider response':
        print('协议类型', 'provider response')
        return {'code': '1000', 'type': 'provider response'}
    elif protocol['type'] == 'call provider':
        print('协议类型', 'call provider')
        return {'code': '1000', 'type': 'call provider'}
