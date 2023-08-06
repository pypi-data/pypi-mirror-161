#!/bin/env python3
# coding:utf-8
"""
    Mgnt Servers主机组内主机与其他主机组做序列号匹配,
    匹配上的把普通主机的inventory OOB IP address的值
    设置为 Mgnt Servers主机 snmp interface的地址
"""

import argparse
import logging
from zabbix_api import ZabbixAPIException

from lib.utils.inventory_tag import InventoryTagDict

parser = argparse.ArgumentParser("Matching inventory OOB IP address")
# parser.add_argument('-g', '--group_name', help='Specify a group name')
parser.add_argument('--rm_auto_oob', action='store_true',
    help='Remove auto_oob in inventory tag field and reset the oob_ip inventory field')
parser.add_argument('--rm_auto_server', action='store_true',
    help='Remove auto_server=x.x.x.x in inventory tag field')
parser.add_argument('--tags', action='store_true',
    help='Make server and bmc host inventory tag')
parser.set_defaults(handler=lambda args: main(args))


def rm_auto_oob_host_inventory_tag(zapi):
    hosts = zapi.host.get({
        'output': ['hostid'],
        'selectInventory': ['tag', 'oob_ip'],
        'searchInventory': {'tag': 'auto_oob'}
    })
    logging.info(f'{len(hosts)} hosts have auto_oob tag')
    for host in hosts:
        itd = InventoryTagDict(host['inventory']['tag'])
        del itd['auto_oob']
        logging.info(f'Updating {host} inventory tag and oob_ip for remove auto_oob tag and oob_ip')
        zapi.host.update({
            'hostid': host['hostid'], 
            'inventory': {'tag': str(itd), 'oob_ip':'' }
        })

def rm_auto_server_host_inventory_tag(zapi):
    hosts = zapi.host.get({
        'output': ['hostid'],
        'selectInventory': ['tag'],
        'searchInventory': {'tag': 'auto_server'}
    })
    logging.info(f'{len(hosts)} hosts have auto_server tag')
    for host in hosts:
        itd = InventoryTagDict(host['inventory']['tag'])
        del itd['auto_server']
        logging.info(f'Updating {host} inventory tag for remove auto_server tag')
        zapi.host.update({
            'hostid': host['hostid'], 
            'inventory': {'tag': str(itd)}
        })

def get_server_bmc_hosts(zapi):

    def get_hosts_by_inventory_type(inventory_type):
        return list(
            filter(
                lambda x: len(x['inventory']['serialno_a']) and len(x['interfaces']),  
                zapi.host.get({
                    'output': ['hostid', 'name'],
                    'selectInventory': ['tag', 'serialno_a'],
                    'selectInterfaces': ['type', 'main', 'ip'],
                    # 'groupids': [item['groupid'] for item in plain_groups]
                    'searchInventory': {'type': inventory_type},
                })
            )
        )
        # return zapi.host.get({
        #     'output': ['hostid', 'name'],
        #     'selectInventory': ['tag', 'serialno_a'],
        #     'selectInterfaces': ['type', 'main', 'ip'],
        #     # 'groupids': [item['groupid'] for item in plain_groups]
        #     'searchInventory': {'type': inventory_type},
        # })

    return get_hosts_by_inventory_type('Server'), get_hosts_by_inventory_type('BMC')

def handle_hosts_tag(zapi):
    server_hosts, bmc_hosts = get_server_bmc_hosts(zapi)
    logging.info(f'Get validate {len(server_hosts)} Server hosts and {len(bmc_hosts)} BMC hosts')

    server_serials = [ item['inventory']['serialno_a'] for item in server_hosts ]
    bmc_serials = [ item['inventory']['serialno_a'] for item in bmc_hosts ]
    server_serial_dict = dict(zip(server_serials, server_hosts))
    bmc_serial_dict = dict(zip(bmc_serials, bmc_hosts))
    
    match = list(set(server_serials) & set(bmc_serials))
    logging.info(f'The number of {len(match)} serialno matched between Server and BMC hosts')
    for serialno in match:
        server_host = server_serial_dict[serialno]
        bmc_host = bmc_serial_dict[serialno]
        logging.info(f'The serialno_a {serialno} is matched between server {server_host["name"]} and bmc {bmc_host["name"]}')

        # 更新Server 主机清单的tag和oob_ip字段
        if len(bmc_host['interfaces']):
            itd = InventoryTagDict(server_host['inventory']['tag'])
            itd['auto_oob'] = None
            zapi.host.update({
                'hostid': server_host['hostid'],
                'inventory': {
                    'tag': str(itd),
                    'oob_ip': bmc_host['interfaces'][0]['ip']
                }
            })

        # 更新MBC 主机清单的tag字段
        if len(server_host['interfaces']):
            itd = InventoryTagDict(bmc_host['inventory']['tag'])
            itd['auto_server'] = server_host['interfaces'][0]['ip']
            zapi.host.update({
                'hostid': bmc_host['hostid'],
                'inventory': {
                    'tag': str(itd)
                }
            })


def main(args):

    zapi = args.zapi

    # 清除实体服务器inventory tag字段中的auto_oob标识
    if args.rm_auto_oob:
        rm_auto_oob_host_inventory_tag(zapi)

    # 清除BMC的inventory tag字段中的auto_server标识
    if args.rm_auto_server:
        rm_auto_server_host_inventory_tag(zapi)

    # 设置Server的auto_oob和BMC的auto_server inventory tag
    if args.tags:
        handle_hosts_tag(zapi)


   
