import re
import argparse
import pandas as pd
import numpy as np
from openpyxl.utils import get_column_letter

parser = argparse.ArgumentParser('Export discovered hosts to excel')
parser.add_argument('-r', '--drule',  help='discovery rule')
parser.add_argument('-o', '--output', help='output save to an excel file, xx.xlsx')
parser.set_defaults(handler=lambda args: main(args))

# 设置excel自动列宽
def to_excel_auto_column_weight(df, writer, sheet_name="Sheet1"):
    """
    DataFrame保存为excel并自动设置列宽
    """
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    # 计算每列表头的字符宽度
    column_widths = (
        df.columns.to_series().apply(lambda x: len(x.encode('utf8'))).values
    )
    # 计算每列的最大字符宽度
    max_widths = (
        df.astype(str).applymap(lambda x: len(x.encode('utf8'))).agg(max).values
    )

    widths = np.max([column_widths, max_widths], axis=0)
    worksheet = writer.sheets[sheet_name]
    for i, width in enumerate(widths, 1):
        # openpyxl设置字符宽度时会缩水0.5左右个字符，所以+2使左右都空出一个字宽。
        worksheet.column_dimensions[get_column_letter(i)].width = width + 2

def main(args):

    zapi = args.zapi
    rules = zapi.drule.get({
        'output': 'extend',
        'selectDChecks': 'extend',
        'selectDHosts': 'extend',
        'search': {
            'name': args.drule
        },
        'searchWildcardsEnabled': True,
    })

    icmp_ping_check_ids = [check['dcheckid'] for rule in rules for check in rule['dchecks'] if check['type'] == '12']
    zabbix_agent_check_ids = [check['dcheckid'] for rule in rules for check in rule['dchecks'] if check['type'] == '9']

    # 正则匹配总类-业务网类-负责人
    pattern = re.compile(r'([^-]+)-([^-]+)-([^-]+)')

    df = pd.DataFrame(columns=['dhostid', 'check_type','ipv4', 'monitored', 'host', 'status', 'multi_inf', 'os', 'net', 'poc'])

    # 获取 Hypervisors 组内host name
    hyperv_grp = zapi.hostgroup.get({'filter': {'name':'Hypervisors'},'selectHosts': ['name']})
    hyperv_hosts = [h['name'] for grp in hyperv_grp for h in grp['hosts']]
    
    # 获取 dservice \ drule name \ Host
    dservices = zapi.dservice.get({
        'output': ['dcheckid', 'ip', 'status', 'value', 'dhostid'],
        'druleids': [rule['druleid'] for rule in rules],
        'selectDRules': ['name'],
        'selectHosts': ['host', 'status'],
    })


    for dservice in dservices:

        info = {}

        # icmp check
        if dservice['dcheckid'] in icmp_ping_check_ids:

            info['dhostid'] = dservice['dhostid']
            info['check_type'] = 'icmp'
            info['ipv4'] = dservice['ip']

            if dservice['hosts']:
                info['monitored'] = '是'     # 是否被监控
                info['host'] = dservice['hosts'][0]['host'] # 监控主机\状态
                info['status'] = ('启用' if dservice['hosts'][0]['status'] == '0' else '禁用')

            elif dservice['ip'] in hyperv_hosts:
                t = zapi.host.get({'filter': {'name': dservice['ip']}, 'selectInventory': ['poc_1_name', 'os_short']})
                zbx_host = t[0]
                info['monitored'] = '是'
                info['host'] = zbx_host['host']
                info['status'] = ('启用' if zbx_host['status'] == '0' else '禁用')
                info['poc'] = zbx_host['inventory'].get('poc_1_name')
                info['os'] = zbx_host['inventory'].get('os_short')


        # agent check
        if dservice['dcheckid'] in zabbix_agent_check_ids:

            info['dhostid'] = dservice['dhostid']
            info['check_type'] = 'agent'
            info['ipv4'] = dservice['ip']

            # 验证是否在zabbix host中
            t = zapi.host.get({'filter': {'host': dservice['value']}, 'selectInventory': ['poc_1_name', 'os_short']})
            
            if t:
                zbx_host = t[0]
                info['host'] = dservice['value']
                info['monitored'] = '是'
                info['status'] = ('启用' if dservice['status'] == '0' else '禁用')  
                info['poc'] = zbx_host['inventory'].get('poc_1_name')
                info['os'] = zbx_host['inventory'].get('os_short')
          
        if info:
            # rule name符合"总类-业务网类-负责人"形式，提取出业务网络和负责人信息
            drule_name = dservice['drules'][0]['name']
            if pattern.search(drule_name):
                _, net, poc = pattern.findall(drule_name)[0]

                # 如从inventory中取到了poc, 则优先使用, 否则使用rule name中的负责人
                info['poc'] = info.get('poc') and info['poc'] or poc
                info['net'] = net

            row = pd.Series(info)
            df = df.append(row, ignore_index=True)


    # 既有icmp check 又有agent check的情况, dhostid相同, 通过check_type排序后, 
    # 去除icmp check的那一行数据, 以agent check为准
    df = df.sort_values(['dhostid', 'check_type'], ascending=False).drop_duplicates(subset='dhostid', keep='last')

    # 按照host进行group by, 其余字段进行单元格合并, (仅host不为空的行参与)
    # 如果同一host有多个不同ipv4, 则认为是多网卡(有可能是一张物理网卡使用多个ip)
    df2 = df.groupby('host', as_index=False).apply(lambda x: pd.Series({
        'ipv4': ','.join(x.ipv4.unique()),
        'monitored': ','.join([i for i in x.monitored.unique() if isinstance(i, str)]),
        'status': ','.join([i for i in x.status.unique() if isinstance(i, str)]),
        'multi_inf': ('是' if x.ipv4.count() > 1 else '否'),
        'net': ','.join([i for i in x.net.unique() if isinstance(i, str)]),
        'poc': ','.join([i for i in x.poc.unique() if isinstance(i, str)]),
        'os': ','.join([i for i in x.os.unique() if isinstance(i, str)]),
    }))


    # 将df中host为空的数据与 df2拼接在一起
    res = df[df.host.isna()].drop(['dhostid', 'check_type'], axis=1).append(df2).reset_index(drop=True)
    res.sort_values(by=['host'], na_position='last', inplace=True)
    res.monitored.fillna('否', inplace=True)
    res.multi_inf.fillna('否', inplace=True)

    # 字段重命名为中文
    res.rename(columns={
        'ipv4': 'ipv4(s)',
        'host': '监控主机',
        'monitored': '是否监控',
        'status': '监控状态',
        'multi_inf': '是否多网卡',
        'net': '网段名称',
        'poc': '负责人',
        'os': '操作系统',
    }, inplace=True)

    # 设置屏幕输出的参数
    pd.set_option('display.width', 180)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', 99)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    print(res)

    if args.output:
        fname = args.output.endswith('.xlsx') and args.output or args.output + '.xlsx'
        writer = pd.ExcelWriter(fname)
        to_excel_auto_column_weight(res, writer, 'discovery数据')
        writer.save()
