import re
import json
import argparse
import logging
import pandas as pd
import numpy as np
import IPy
from zabbix_api import ZabbixAPIException
from openpyxl.utils import get_column_letter

parser = argparse.ArgumentParser('find ip from host inventory')
parser.add_argument('-f', '--check_file', required=True, help='a list of ip range of each IDC')
parser.add_argument('--dump', choices=['console', 'excel'], default='console', help='Print to screen, or save to excel')
group = parser.add_mutually_exclusive_group()  # 互斥参数组, 组内参数不能同时出现
group.add_argument('--check_agent', action='store_true', help='display invalid interface')
group.add_argument('--delete_invalid', action='store_true', help='delete invalid interface')
group.add_argument('--add_extra', action='store_true', help='add extra ip to interface')
group.add_argument('--delete_extra', action='store_true', help='delete extra ip from interface')
parser.set_defaults(handler=lambda args: main(args))

# 匹配windows和linux ip的正则表达式
win_host_ptn = re.compile(r'windows', re.I)
linux_host_ptn = re.compile(r'linux', re.I)
linux_ip_ptn = re.compile(r'((?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))(?:\/(?:\d|[1-2]\d|3[0-2]))', re.M)
win_ip_ptn = re.compile(r'((?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))', re.M)


# 各机房网段信息
IDC_NETWORKS = []

def main(args):

    zapi = args.zapi

    # 读取ip_range.json各机房ip网段
    global IDC_NETWORKS
    with open(args.check_file, 'r', encoding='utf8')as fp:
        for _, networks in json.load(fp).items():
            IDC_NETWORKS +=  [IPy.IP(net) for net in networks]


    zbx_host = zapi.host.get({
        'output':['name', 'hostid', 'proxy_hostid'],
        'selectInventory':['inventory_mode', 'location', 'host_networks', 'os_full', 'os_short'],
        'selectInterfaces':['interfaceid', 'ip', 'type', 'main'],
       #'filter': {'host':'1.1.1.3'},
    })



    # 生成pandas数据表, 用来输出屏幕和保存文件
    df = pd.DataFrame(columns=['zbx_host', 'os', 'location', 'agent_interfaces', 'other_ipv4s'])


    for host in zbx_host:

        location = host['inventory'].get('location')
        zbx_host = host['name']
        os_short= host['inventory'].get('os_short', '')

        # 指定了--delete_invalid, 删除主机中无效的agent interfaces
        if args.delete_invalid:
            delete_invaild(zapi, host)

        # 指定了--delete_extra, 只保留第一个agent interfaces，其余的全部删除
        if args.delete_extra:
            delete_extra(zapi, host)


        # 指定了--add_extra, 将额外的主机地址添加到host agent interface
        if args.add_extra:
            add_extra(zapi, host)


        # 指定了--check_agent, 过滤出IP地址不存在于主机资产的agent interface
        if args.check_agent:
            agent_ips = check_agent(host)
            if not agent_ips:
                logging.debug(f"All agent interfaces of host->{host['name']} are in host_networks")
                continue
        else:
            agent_ips = get_agent_ips(host)

        other_ips = get_other_ips(host)

        # 添加数据到数据表
        df.loc[len(df)] = [zbx_host, os_short, location, ','.join(agent_ips), ','.join(other_ips)]

    # 将结果按location排序
    res = df.sort_values(by=['location'], na_position='last').reset_index(drop=True)
    if res.empty:
        logging.info('No data retrieved.')
        exit()

    if args.dump == 'excel':
        save_to_excel(res, 'result.xlsx')
    elif args.dump == 'console':
        # 设置屏幕输出列对齐
        pd.set_option('display.width', 180)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', 99)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        print(res)




def to_excel_auto_column_weight(df, writer, sheet_name="Sheet1"):
    """
    DataFrame保存为excel并自动设置列宽
    """
    df.to_excel(writer, sheet_name=sheet_name, index=False)

    column_widths = (
        df.columns.to_series().apply(lambda x: len(x.encode('utf8'))).values
    )
    max_widths = (
        df.astype(str).applymap(lambda x: len(x.encode('utf8'))).agg(max).values
    )

    widths = np.max([column_widths, max_widths], axis=0)
    worksheet = writer.sheets[sheet_name]
    for i, width in enumerate(widths, 1):
        worksheet.column_dimensions[get_column_letter(i)].width = width + 2


def valid_ip(ip):
    """
    验证ip是否在各机房网段内
    """
    global IDC_NETWORKS

    if ip and IDC_NETWORKS:
        for net in IDC_NETWORKS:
            if ip in net:
                return True
    return False


def get_agent_ips(host) -> list:
    """
    获取 zabbix agent interfaces ip
    """
    agent_interfaces = [inf for inf in host['interfaces'] if inf['type'] == '1']
    return [inf['ip'] for inf in agent_interfaces]


def get_host_networks(host) -> set:
    """
    获取inventory中host_networks里面的ip地址
    """
    global win_host_ptn, linux_host_ptn, win_ip_ptn, linux_ip_ptn

    os_full = host['inventory'].get('os_full', '')
    if win_host_ptn.search(os_full):
        host_networks = set(win_ip_ptn.findall(host['inventory'].get('host_networks','')))
    elif linux_host_ptn.search(os_full):
        host_networks = set(linux_ip_ptn.findall(host['inventory'].get('host_networks','')))
    else:
        host_networks = set()  # 无法判断windows、linux
    return host_networks


def get_other_ips(host) -> list:
    """
    inventory 中 host_networks里面的ip 排除掉agent_ips,
    再排除掉不在IDC_NETWORKS网段内的ip
    """
    agent_ips = get_agent_ips(host)
    host_networks = get_host_networks(host)
    other_ips = list(host_networks - set(agent_ips))
    return [ip for ip in other_ips if valid_ip(ip)]


def delete_invaild(zapi, host) -> None:
    """
    删除ip不在 host_networks中的非第一个agent interface
    """
    host_networks = get_host_networks(host)
    if not host_networks:
        return

    for inf in host['interfaces'][::-1]:
        if inf['type'] == '1' and inf['main'] != '1':
            if inf['ip'] in host_networks:
                continue
            try:
                zapi.hostinterface.delete([inf['interfaceid']])
                logging.info(f"Invalid agent interface deleted: host->{host['name']}, agent_ip->{inf['ip']}")
                host['interfaces'].remove(inf)
            except ZabbixAPIException:
                logging.error(f"Delete agent interface failed: host->{host['name']}, agent_ip->{inf['ip']}")


def delete_extra(zapi, host) -> None:
    """
    指定了--delete_extra, 只保留第一个agent interfaces，其余的全部删除
    """
    for inf in host['interfaces'][::-1]:
        if inf['type'] == '1' and inf['main'] != '1':
            try:
                zapi.hostinterface.delete([inf['interfaceid']])
                logging.info(f"Extra agent interface deleted: host->{host['name']}, agent_ip->{inf['ip']}")
                host['interfaces'].remove(inf)
            except ZabbixAPIException:
                logging.error(f"Delete agent interface failed: host->{host['name']}, agent_ip->{inf['ip']}")


def add_extra(zapi, host) -> None:
    """
    将额外的主机地址添加到host agent interface
    """
    for ip in get_other_ips(host):
        try:
            zapi.hostinterface.create({
                'hostid': host['hostid'],
                'dns': '',
                'ip': ip,
                'main': 0,
                'port': '10050',
                'type': 1,
                'useip': 1
            })
            logging.info(f"Successfully added interface: host->{host['name']}, extra_ip->{ip}")
            host['interfaces'].append({'main': '0', 'type': '1', 'ip': ip})
        except ZabbixAPIException:
            logging.error(f"Add interface faild! host->{host['name']},extra_ip->{ip}")


def check_agent(host) -> list:
    """
    打印agent interface IP地址不存在于主机资产的host_networks的信息
    """
    host_networks = get_host_networks(host)
    if not host_networks: # host_networks未匹配出ip
        logging.debug(f"host->{host['name']} has no host_networks, skipped.")
        return []

    agent_ips = get_agent_ips(host)
    return [ip for ip in agent_ips if  ip not in host_networks]


def save_to_excel(df: pd.DataFrame, fname: str):
    if not fname.endswith('.xlsx'):
        fname = fname + '.xlsx'

    writer = pd.ExcelWriter(fname)
    to_excel_auto_column_weight(df, writer)
    writer.save()
    logging.info(f"Successfully saved file to {fname}")
