#!/bin/env python3
# coding:utf-8
"""
    从企业微信中获取用户ID，更新到zabbix用户的企业微信告警媒介的sendto
"""

import sys
import argparse
import logging
import os
from functools import reduce
from lib.utils.wework import SyncWeworkMedia


parser = argparse.ArgumentParser()
parser.add_argument('--corpid', help='企业微信的企业ID')
parser.add_argument('--secret', help='企业微信内应用的Secret')
parser.add_argument('-t', '--token-cache', help='从本地文件读取access_token')
parser.add_argument('-d', '--depart-name', help='指定企业微信中部门名称')
parser.add_argument('-e', '--env', action='store_true', help='从环境变量中读取参数')
parser.add_argument('-g', '--usergroups', nargs='+', action='append', help='指定更新的zabbix用户组')
parser.add_argument('--username', help='指定更新的zabbix用户')
parser.add_argument('--allow-update', action='store_true', help='当zabbix user已存在企业微信告警媒介, \
但sendto字段与获取的企业微信userid不一致, 是否允许更新')
parser.set_defaults(handler=lambda args: main(args))


def main(args):
    # print(args)
    corpid = args.corpid
    secret = args.secret
    token = None

    # 从环境变量中读取参数, 优先级小于命令行指定的参数
    if args.env:
        corpid = corpid if corpid else os.environ.get('WEWORK_CORPID')
        secret = secret if secret else os.environ.get('WEWORK_SECRET')
        token = os.environ.get('WEWORK_TOKEN')

    if args.token_cache:
        try:
            with open(args.token_cache, mode='r', encoding='utf-8') as f:
                token = f.readline()
        except Exception as e:
            logging.warning(e)

    if corpid and secret:

        corpapi = SyncWeworkMedia.create_corpapi(corpid, secret, token)

        zbx_user_group_ids = reduce(lambda x, y:x + y ,args.usergroups) if args.usergroups else []

        worker = SyncWeworkMedia(zapi=args.zapi,
                        corpapi=corpapi,
                        depart_name=args.depart_name,
                        zbx_usrgrps=zbx_user_group_ids,
                        zbx_username=args.username,
                        allow_update=args.allow_update)
        worker.run()
        worker.show()
    else:
        parser.print_help()
        logging.error('Missing key parameters `corpid` and `secret`')
        sys.exit(1)
