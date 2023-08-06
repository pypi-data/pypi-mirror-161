#!/bin/env python3
# coding:utf-8
"""
    添加/删除/显示 主机模板
"""

import argparse
import logging
from lib.utils.TemplateTool import *

# 设置子命令和可选参数
parser = argparse.ArgumentParser("(list|add|del) zabbix hosts' templates")
parser.add_argument('--hosts', nargs='+', help="specific zabbix hosts")
parser.add_argument('--groups', nargs='+', help="specific zabbix hostgroups")
parser.add_argument('--to', nargs='+', help='specific templates names instead to')

opt_group = parser.add_mutually_exclusive_group(required=True)
opt_group.add_argument('--list', action='store_true', help="list specific hosts' templates")
opt_group.add_argument('--add', nargs='+', help="add specific hosts' templates")
opt_group.add_argument('--clear', nargs='+', help="del specific hosts' templates")
opt_group.add_argument('--use', nargs='+', help="use specific hosts' templates")
opt_group.add_argument('--replace', nargs='+', help="replace specific hosts' templates")

parser.set_defaults(handler=lambda args:main(args))

def main(args: dict) -> None:
    # 显示模板信息
    if args.list:
        ListTemplate(args)
    # 添加模板
    if args.add:
        AddTemplate(args)
    # 移除指定模板
    if args.clear:
        ClearTemplate(args)
    # 替换全部模板
    if args.use:
        UseTemplate(args)
    # 替换指定模板
    if args.replace:
        if not args.to:
            parser.print_help()
            logging.error('the argument --to is required')
            exit(-1)
        ReplaceTemplate(args)
