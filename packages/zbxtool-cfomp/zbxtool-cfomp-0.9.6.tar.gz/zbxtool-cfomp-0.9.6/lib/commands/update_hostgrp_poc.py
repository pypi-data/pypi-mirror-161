#!/bin/env python3
# coding:utf-8
"""
    配置主机组的联系人信息，更新到主机组内主机的inventory
"""
import json
import argparse
import ldap3
import logging

parser = argparse.ArgumentParser('Access ldap server and update zabbix host inventory poc')
parser.add_argument('-c', '--contacts-file', required=True, help='HostGroup contacts file')
parser.add_argument('-l', '--ldap-server', required=True, help='ldap server ip address')
parser.add_argument('-o', '--ldap-port', default=389, help='ldap server port')
parser.add_argument('-b', '--ldap-user', required=True, help='ldap bind user')
parser.add_argument('-w', '--ldap-password', required=True, help='ldap password')
parser.set_defaults(handler=lambda args: main(args))

class LdapServer():
    """
    使用 ldap3 模块连接ldap server, 通过 dn 查询用户对应的属性
    """
    def __init__(self, host, port, bind_user, password):
        self.__server = ldap3.Server(host=host, port=port)
        self.__conn = ldap3.Connection(self.__server, bind_user, password, auto_bind=True)

    def get_user_info(self, dn):
        if not dn:
            return {}
        res = self.__conn.search(
            search_base=dn,
            search_filter='(objectClass=*)',
            search_scope=ldap3.BASE,
            attributes=ldap3.ALL_ATTRIBUTES  # 该参数无法取消, 取消后不返回任何属性
        )
        if res:
            return self.__conn.response[0].get('attributes')
        return {}


def main(args):
    """
    读取 Contacts.json 文件中 HostGroup 联系人信息, 按 GroupName 升序排列
    遍历 HostGroup 并将 zabbix 中对应的 Host 更新 Poc 信息。
    """

    contacts_file = args.contacts_file
    contacts = {}

    # 读取文件中 HostGroup 联系人信息, 生成contacts, [{group1's info}, {group2's info}, ...]
    with open(contacts_file, 'r', encoding='utf8')as fp:
        temp = json.load(fp)
        for info in temp['HostGroup']:
            contacts[info['GroupName']] = info

    zapi = args.zapi

    zbx_groups = zapi.hostgroup.get({
        'output': ['groupid', 'name'],
        'selectHosts': ['hostid'],
        'filter': {'name': list(contacts.keys())}
    })

    # 登录ldap server
    ldap = LdapServer(host=args.ldap_server,
                      port=args.ldap_port,
                      bind_user=args.ldap_user,
                      password=args.ldap_password)

    # 将zbx_groups 按照 group name 升序排列
    zbx_groups.sort(key=lambda g: g.get('name'))

    for zbx_group in zbx_groups:
        contact = contacts.get(zbx_group.get('name'), {})
        poc_1_dn = contact.get('poc_1_dn')
        poc_2_dn = contact.get('poc_2_dn')
        ldap.get_user_info(poc_1_dn)
        ldap.get_user_info(poc_2_dn)
        poc_1_info = ldap.get_user_info(poc_1_dn)
        poc_2_info = ldap.get_user_info(poc_2_dn)

        zapi.host.massupdate({
            'hosts': zbx_group.get('hosts'),
            'inventory_mode': 1,  # 1 - Automatic
            'inventory': {
                'poc_1_name': ''.join(poc_1_info.get('sn', '') + poc_1_info.get('givenName', '')),
                'poc_1_email': ','.join(poc_1_info.get('mail', '')),
                'poc_1_phone_a': poc_1_info.get('telephoneNumber', [''])[0],
                'poc_1_phone_b': poc_1_info.get('telephoneNumber', [''])[-1],
                'poc_1_cell': ','.join(poc_1_info.get('mobile', '')),
                'poc_1_screen': ','.join(poc_1_info.get('uid', '')),
                'poc_1_notes': '',  # ldap暂无设置此属性
                'poc_2_name': ''.join(poc_2_info.get('sn', '') + poc_2_info.get('givenName', '')),
                'poc_2_email': ','.join(poc_2_info.get('mail', '')),
                'poc_2_phone_a': poc_2_info.get('telephoneNumber', [''])[0],
                'poc_2_phone_b': poc_2_info.get('telephoneNumber', [''])[-1],
                'poc_2_cell': ','.join(poc_2_info.get('mobile', '')),
                'poc_2_screen': ','.join(poc_2_info.get('uid', '')),
                'poc_2_notes': ''  # ldap暂无设置此属性
            }
        })
        logging.info(f"update success! HostGroup-> [{zbx_group.get('name')!r}] ")
