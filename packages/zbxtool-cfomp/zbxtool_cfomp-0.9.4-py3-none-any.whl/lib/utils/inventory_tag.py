import re
import collections


def _safe_tag_literal(ori: str):
    res = ori.replace('=', '\\3D')
    res = res.replace(';', '\\3B')
    return res.strip()


def parse_inventory_tag_literal(inventory_tag):
    res = {}

    if inventory_tag == None:
        return res

    if not isinstance(inventory_tag, str):
            raise TypeError()

    tags = inventory_tag.strip().split(';')

    for item in tags:

        item = item.strip()
        pos = item.find('=')
        if pos < 0:
            key = item.rstrip()
            if len(key) > 0:
                res[key] = None
        elif pos > 0:
            key = item[0: pos]
            val = item[pos+1 : ]
            key = key.rstrip()
            val = val.lstrip()
            if len(key) > 0:
                res[key] = val

    return res

class InventoryTagDict(collections.UserDict):
    """
    由于Zabbix 4.0版本host不支持tag功能，缓解方法是在host inventory的tag字段定稿相应的tag
    inventory tag的格式规范是以分号分隔的k=v或者k字符串，示例如下：
        key1=val1;key2;key3=val3
    """
    def __init__(self, inventory_tag=None):
        super().__init__(parse_inventory_tag_literal(inventory_tag))

    def __setitem__(self, key, item):
        '''
        value的数据类型必须为字符串或者None，不支持其它复杂的数据类型
        '''
        if not isinstance(item, str) and item != None:
            raise TypeError()
        super().__setitem__(key, item)
        
    def __str__(self):
        res = ''
        for k,v in self.data.items():

            res += _safe_tag_literal(k)
            if v:
                res += ('=' + _safe_tag_literal(v))
            res += ';'

        return res