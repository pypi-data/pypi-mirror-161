"""
子模块读取
"""

from importlib import import_module
from sys import path as sys_path


class ReadModule:
    def __init__(self, path=None):
        if path is None:
            path = '..'
        sys_path.append(path)
        self.module_list = {}

    def read(self, item):
        if item in self.module_list.keys():
            return self.module_list[item]
        module_item = import_module(item)
        self.module_list[item] = module_item
        return module_item
