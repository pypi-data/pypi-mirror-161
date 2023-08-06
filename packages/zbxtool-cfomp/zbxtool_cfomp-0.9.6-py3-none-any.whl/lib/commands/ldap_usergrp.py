#!/bin/env python3
# coding:utf-8
"""
    为zabbix每个主机组创建用户组,
    zabbix用户组及其成员信息同步至lad中。
"""

import argparse
import logging
import ldap3
from zabbix_api import ZabbixAPIException
from lib.utils.LdapTool import Ldap

parser = argparse.ArgumentParser()
parser.add_argument('--create-ldap-group', action='store_true')
parser.add_argument('--create-zbx-usrgrp', action='store_true')
parser.add_argument('--clean', action='store_true')
parser.add_argument('-l', '--ldap-server', required=True, help='ldap server ip address')
parser.add_argument('-o', '--ldap-port', default=389, help='ldap server port')
parser.add_argument('-b', '--ldap-user', required=True, help='ldap bind user')
parser.add_argument('-w', '--ldap-password', required=True, help='ldap password')
parser.set_defaults(handler=lambda args: main(args))

# ldap搜索dn
LDAP_USER_GROUP_DN = 'ou=user groups,ou=zabbix,dc=shchinafortune,dc=local'
LDAP_USER_DN = 'ou=Person,dc=shchinafortune,dc=local'

def main(args):

    zapi = args.zapi
    ldap = Ldap(args.ldap_server, args.ldap_user, args.ldap_password, args.ldap_port)

    # 1.取zbx主机组
    zbx_hostgrps = zapi.hostgroup.get({
        'output': ['name'],
        'filter': {'flag': 0, 'internal': 0},
        'monitored_hosts': 1
    })

    # 2.取zbx用户组
    zbx_usergrps = zapi.usergroup.get({
        'searchWildcardsEnabled': True,
        'output': ['name'],
        'selectUsers': ['userid', 'alias', 'name', 'surname']
    })

    # 3.筛选出zbx中没有用户组的主机组
    usergrp_names = [usergrp['name'].replace(' admins', '') for usergrp in zbx_usergrps]
    zbx_hostgrps_without_usergrp = filter(lambda g: g['name'] not in usergrp_names, zbx_hostgrps)

    # 4.为上一步筛出的zbx主机组创建用户组
    if args.create_zbx_usrgrp:

        for hostgrp in zbx_hostgrps_without_usergrp:
            try:
                grp_name = hostgrp['name'] + ' admins'

                res = zapi.usergroup.create({
                    'name': grp_name,
                    'rights': {'id': hostgrp['groupid'], 'permission': 3}
                })

                # 同时追加至zbx_usergrps
                zbx_usergrps.append({'usrgrpid': ''.join(res['usrgrpids']), 'name': grp_name, 'users': []})
                logging.info(f'Create zabbix userGroup-> `{grp_name}` success!')

            except ZabbixAPIException as err:
                logging.error(err)


    # 清除ldap中zabbix用户组
    if args.clean:
        logging.info('clean ldap user group `{}`'.format(LDAP_USER_GROUP_DN))
        ldap.clean_usergrp(LDAP_USER_GROUP_DN)

    # 5.更新/新建ldap group
    if args.create_ldap_group:

        logging.info('update ldap user group `{}`'.format(LDAP_USER_GROUP_DN))
        for zbx_grp in zbx_usergrps:

            # 新的成员列表
            uniqueMember = []

            # 判断zabbix用户是否存在于ldap中, 添加至成员列表
            for user in zbx_grp['users']:
                res = ldap.search_user(LDAP_USER_DN, user['alias'])
                if res:
                    uniqueMember.append(res)


            zbx_grp_name  = zbx_grp['name'].replace('(', '\\28').replace(')', '\\29') # 特殊字符需进行处理

            search_res = ldap.search_usergrp(LDAP_USER_GROUP_DN, zbx_grp_name)

            if search_res:
                ldap.update_member(search_res[0], uniqueMember)
            else:
                cn = 'cn=%s,%s' % (zbx_grp_name, LDAP_USER_GROUP_DN)
                ldap.create_usergrp(cn, uniqueMember)

