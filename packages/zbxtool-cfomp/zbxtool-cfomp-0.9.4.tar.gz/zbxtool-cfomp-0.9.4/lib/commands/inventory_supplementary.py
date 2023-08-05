#!/bin/env python3
# coding:utf-8
"""
检索 "Chassis Model" 监控项，如果最新值包含 "VMware" "KVM", 把inventory type字段设置为VM
检索监控项key为proc.num[rsync,root,,--daemon]的主机，如果监控项最新值为1，在inventory tag中添加rsyncd标签，
如果为0，删除在inventory tag中rsyncd标签
"""
import argparse
import logging
from zabbix_api import ZabbixAPIException
from lib.utils.inventory_tag import InventoryTagDict

parser = argparse.ArgumentParser()
parser.set_defaults(handler=lambda args: main(args))

def is_vm(_, item: dict) -> bool:
    """判断字符串是否包含'VMware', 'KVM'"""
    keywords = ['VMware', 'KVM']
    for k in keywords:
        if k in item['lastvalue']:
            return True
    return False

def is_host(item: dict) -> bool:
    """判断该item为host的item, 排除template的item"""
    return item['hosts'][0]['status'] != '3'


class UpdateInventory:
    """更新zabbix inventory"""
    # item.get的参数
    query_params = {}
    # item结果进行过滤的函数
    filter_func = None

    def __init__(self, zapi):
        self.zapi = zapi
        self.items = None
        self.get_items()
        self.update_host()

    def get_items(self):
        """获取items"""
        if self.query_params:
            self.items = self.zapi.item.get(self.query_params)

        # 过滤掉host类型为模板的情况
        self.items = [i for i in self.items if is_host(i)]

        # 执行指定的过滤
        if self.filter_func:
            self.items = [i for i in self.items if self.filter_func(i)]

    def update_host(self):
        """获取以上items的host信息, 更新inventory"""
        for item in self.items:
            hosts_info = self.zapi.host.get({
                'output': ['host'],
                'hostids': [h['hostid'] for h in item['hosts']],
                'selectInventory': "extend"
            })

            # 更新host的inventory
            for host in hosts_info:
                update_params = {'hostid': host['hostid']}
                update_params['inventory'] = self.gen_inventory(item, host)

                # 如inventory mode为禁用, 则改为自动
                if host['inventory']['inventory_mode'] == '-1': # disabled
                    update_params['inventory_mode'] = '1'       # automatic
                try:
                    self.zapi.host.update(update_params)
                    logging.info('update host->%s success!', host['host'])
                except ZabbixAPIException as err:
                    logging.exception("zapi error: %s", err)

    def gen_inventory(self, item:dict, host:None) -> dict:
        raise NotImplementedError("You need to implement method gen_inventory")


class UpdateInventoryType(UpdateInventory):
    """
    检索 "Chassis Model" 监控项，如果最新值包含 "VMware" "KVM", 把inventory type字段设置为VM
    """
    query_params = {
        'output': ['lastvalue'],
        'selectHosts': ['host', 'status'],
        'filter': {'name': 'Chassis Model'}
    }
    filter_func = is_vm

    def gen_inventory(self, item: dict, host: None) -> dict:
        return {'type': 'VM'}


class UpdateInventoryTag(UpdateInventory):
    """
    检索监控项key为proc.num[rsync,root,,--daemon]的主机，如果监控项最新值为1，在inventory tag中添加rsyncd标签，
    如果为0，删除在inventory tag中rsyncd标签
    """
    query_params = {
        'output': ['lastclock', 'lastvalue'],
        'selectHosts': ['host', 'status'],
        'search': {
            'key_': 'proc.num[rsync,root,,--daemon]'
        }
    }

    def gen_inventory(self, item:dict, host:dict) -> dict:
        tags = InventoryTagDict(host['inventory']['tag'])
        # 如果监控项最新值为1，在inventory tag中添加rsyncd标签，
        if item['lastclock'] != '0' and item['lastvalue'] == '1':
            tags['rsyncd'] = '1'
        # 如果监控项最新值为0，删除inventory tag中的rsyncd标签
        elif item['lastclock'] != '0' and item['lastvalue'] == '0':
            if 'rsyncd' in tags:
                del tags['rsyncd']
        return {'tag': str(tags)}


def main(args):
    zapi = args.zapi
    UpdateInventoryType(zapi)
    UpdateInventoryTag(zapi)
