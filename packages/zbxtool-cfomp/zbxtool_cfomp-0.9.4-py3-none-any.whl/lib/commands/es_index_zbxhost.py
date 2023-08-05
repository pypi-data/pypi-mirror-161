#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
import time
import re
from datetime import datetime
from functools import reduce
from collections.abc import Iterable
from elasticsearch import Elasticsearch, helpers

parser = argparse.ArgumentParser('Gather zabbix host informations and create es index')
parser.add_argument('--es_url', required=True, help="ElasticSearch server ip")
parser.add_argument('--es_user', default='', help="ElasticSearch server login user")
parser.add_argument('--es_passwd', default='', help="ElasticSearch server login password")
parser.set_defaults(handler=lambda args: main(args))

class ItemFilterAndAccumulator(object):

    def __init__(self, keywords):
        if not isinstance(keywords, Iterable):
            raise ValueError('keyworks must be iterabled')
        self.keywords = keywords

    def is_keywords(self, item):
        for word in self.keywords:
            if word not in item['key_']:
                return False
        return True

    def get_result(self, items):
        filtered_items = filter(self.is_keywords, items)
        result = reduce(lambda x, y: x+y, [
                        item['lastvalue'] for item in filtered_items], 0)
        return result if result > 0 else None


def format_items(host):
    if host['flags'] != "4":
        for item in host['items']:
            item['lastvalue'] = float(
                item['lastvalue']) if (item['value_type'] == '0' or item['value_type'] == '3') else item['lastvalue']
        host['filesystems_total'] = ItemFilterAndAccumulator(
            ['vfs.fs.size', 'total']).get_result(host['items'])
        host['filesystems_used'] = ItemFilterAndAccumulator(
            ['vfs.fs.size', 'used']).get_result(host['items'])
        host['memory_total'] = ItemFilterAndAccumulator(
            ['vm.memory.size', 'total']).get_result(host['items'])
        host['memory_used'] = ItemFilterAndAccumulator(
            ['vm.memory.size', 'used']).get_result(host['items'])
    host.pop('items')


# linux 网络接口 ip, 后面却没用到, 不知原因, 先注释
#linux_match = re.compile(
#    r'^ *inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*$', re.M)

# windows 网络接口 ip, 后面却没用到, 不知原因, 先注释
#win_match = re.compile(
#    r'^Ethernet *enabled *(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*$', re.M)

def get_hosts(zapi, es):

    body_datas = []

    hosts = zapi.host.get({
        'output': 'extend',
        'selectGroups': 'extend',
        'selectInterfaces': 'extend',
        'selectInventory': 'extend',
        # 'selectItems': ['name', 'lastvalue', 'value_type', 'key_'],
    })
    dt = time.strftime('%Y.%m.%d', time.localtime())

    for host in hosts:
        host['@timestamp'] = datetime.utcfromtimestamp(time.time())
        # format_items(host)

        host['group_names'] = [group['name'] for group in host['groups']]
        host['ipv4_addresses'] = [aif['ip'] for aif in host['interfaces']]

# 这段代码, 后面却没用到, 不知原因, 先注释
#        ipv4_addresses = linux_match.findall(
#            host['inventory'].get('host_networks', ''), re.M)
#
#        ipv4_addresses = win_match.findall(
#            host['inventory'].get('host_networks', ''), re.M)
#
#        if "127.0.0.1" in ipv4_addresses:
#            ipv4_addresses.remove("127.0.0.1")
#        host['ipv4_addresses'] = ipv4_addresses

        body_datas.append({
            '_id': host['hostid'],
            '主机名称':  host['inventory'].get('name', host['host']),
            '主机别名': host['inventory'].get('alias', host['host']),
            '接口地址': [aif['ip'] for aif in host['interfaces']],
            '主机组': [grp['name'] for grp in host['groups']],
            'OS': host['inventory'].get('os'),
            'OS_FULL': host['inventory'].get('os_full'),
            'OS_SHORT': host['inventory'].get('os_short'),
            '资产标签': host['inventory'].get('asset_tag'),
            '主负责人': host['inventory'].get('poc_1_name'),
            '次负责人': host['inventory'].get('poc_2_name'),
            '机架': host['inventory'].get('chassis'),
            '子网掩码': host['inventory'].get('host_netmask'),
            '主机网络': host['inventory'].get('host_networks'),
            '机房': host['inventory'].get('location'),
            '机柜': host['inventory'].get('site_rack'),
            # '序列号一': host['inventory'].get('serialno_a'),
            '序列号': host['inventory'].get('serialno_a'),
            # '序列号二': host['inventory'].get('serialno_b'),
            '管理IP': host['inventory'].get('oob_ip'),
            'MAC_A': host['inventory'].get('macaddress_a'),
            'MAC_B': host['inventory'].get('macaddress_b'),
            '硬件架构': host['inventory'].get('hw_arch'),
            '标签':  host['inventory'].get('tag'),
            '类型': host['inventory'].get('type'),
            '具体类型': host['inventory'].get('type_full'),
            '型号': host['inventory'].get('model'),
            '供应商': host['inventory'].get('vendor'),
            '@timestamp': datetime.utcfromtimestamp(time.time())
        })

    for host in hosts:
        host['_id'] = host['hostid']
    helpers.bulk(es, hosts, index='zabbix-raw-host-info-' + dt, raise_on_error=True)
    helpers.bulk(es, body_datas, index='zabbix-host-info-' + dt, raise_on_error=True)


def main(args):
    zapi = args.zapi
    es = Elasticsearch(args.es_url, http_auth=(args.es_user, args.es_passwd))
    get_hosts(zapi, es)
