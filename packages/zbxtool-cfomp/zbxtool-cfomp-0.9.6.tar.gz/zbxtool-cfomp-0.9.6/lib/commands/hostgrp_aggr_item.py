"""
在Zabbix server主机创建用于统计各主机组资源使用情况的监控项
包括
【CPU平均利用率】、
【总磁盘空间、已用磁盘空间、磁盘使用率】
【总内存、已使用内存、内存利用率】
"""

import argparse
import logging
import hashlib


parser = argparse.ArgumentParser()
parser.add_argument('hostgroup', nargs='+', help='host group name')
parser.set_defaults(handler=lambda args: main(args))


def create_fs_aggregation_item(api, host, groups):
    """
    创建主机组的总磁盘和已用磁盘空间的Aggregate监控项
    创建主机组的磁盘使用率Calculated监控项
    :param api:
    :param host:
    :param groups:
    :return:
    """
    item = {"delay": 3600,
            "hostid": "",
            "key_": "",
            "name": 'Total disk space in $1',
            # Zabbix aggregate
            "type": 8,
            # numeric unsigned
            "value_type": 3,
            # decimal
            "data_type": 0,
            # "applications": [app["applicationid"] for app in apps],
            "units": "B"
            }

    item["hostid"] = host["hostid"]
    apps = api.application.get({
        'hostids': host["hostid"], 'filter': {'name': 'Filesystem aggregation'}
    })
    item["applications"] = [app["applicationid"] for app in apps]
    for grp in groups:
        item["key_"] = "grpsum[\"%s\",\"vfs.fs.totalsize\",last]" % grp
        item["name"] = f'Total disk space in {grp}'
        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': item["key_"]}
        })
        if len(result) == 0:
            api.item.create(item)
            logging.info(f'{item} creating success')
        else:
            logging.debug(f'{item} already exists')

        item["key_"] = "grpsum[\"%s\",\"vfs.fs.usedsize\",last]" % grp
        item["name"] = f'Used disk space in {grp}'
        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': item["key_"]}
        })
        if len(result) == 0:
            api.item.create(item)
            logging.info(f'{item} creating success')
        else:
            logging.debug(f'{item} already exists')

        cal_item = {"delay": 86400,
                    "hostid": host["hostid"],
                    "key_": hashlib.md5(("%s_used_disk_space_percentage" % grp).encode('utf-8')).hexdigest(),
                    "name": "Used disk space in %s (percentage)" % grp,
                    # calculated
                    "type": 15,
                    # numeric float
                    "value_type": 0,
                    # decimal
                    "data_type": 0,
                    "applications": [app["applicationid"] for app in apps],
                    "units": "%",
                    "params": "100*last(\"grpsum[\\\"%s\\\",\\\"vfs.fs.usedsize\\\",last]\") / " \
                              "last(\"grpsum[\\\"%s\\\",\\\"vfs.fs.totalsize\\\",last]\")" % (grp, grp)
                    }

        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': cal_item["key_"]}
        })
        if len(result) == 0:
            api.item.create(cal_item)
            logging.info(f'{cal_item} creating success')
        else:
            logging.debug(f'{cal_item} already exists')


def create_memory_aggregation_item(api, host, groups):
    """
    创建主机组总内存和已用内存的Aggregate监控项
    创建主机组内存使用率的Calculated监控项
    :param api:
    :param host:
    :param groups:
    :return:
    """
    item = {"delay": 600,
            "hostid": "",
            "key_": "",
            "name": 'Total disk space in $1',
            # Zabbix aggregate
            "type": 8,
            # numeric unsigned
            "value_type": 3,
            # decimal
            "data_type": 0,
            # "applications": [app["applicationid"] for app in apps],
            "units": "B"
            }

    item["hostid"] = host["hostid"]
    apps = api.application.get({
        'hostids': host["hostid"], 'filter': {"name": 'Memory aggregation'}
    })
    item["applications"] = [app["applicationid"] for app in apps]
    for grp in groups:
        item["key_"] = "grpsum[\"%s\",\"vm.memory.size[total]\",last]" % grp
        item["name"] = f'Total memory in group {grp}'
        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': item["key_"]}
        })
        if len(result) == 0:
            api.item.create(item)
            logging.info(f'{item} creating success')
        else:
            logging.debug(f'{item} already exists')

        item["key_"] = "grpsum[\"%s\",\"vm.memory.size[used]\",last]" % grp
        item["name"] = f'Used memory in group {grp}'
        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': item["key_"]}
        })
        if len(result) == 0:
            api.item.create(item)
            logging.info(f'{item} creating success')
        else:
            logging.debug(f'{item} already exists')

        cal_item = {"delay": 3600,
                    "hostid": host["hostid"],
                    #key的名字不能包含中文
                    "key_": hashlib.md5(("%s_used_memory_percentage" % grp).encode('utf-8')).hexdigest(),
                    "name": "Memory utilization in group %s" % grp,
                    # calculated
                    "type": 15,
                    # numeric float
                    "value_type": 0,
                    # decimal
                    "data_type": 0,
                    "applications": [app["applicationid"] for app in apps],
                    "units": "%",
                    "params": "100*last(\"grpsum[\\\"%s\\\",\\\"vm.memory.size[used]\\\",last]\") / " \
                              "last(\"grpsum[\\\"%s\\\",\\\"vm.memory.size[total]\\\",last]\")" % (grp, grp)
                    }

        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': cal_item["key_"]}
        })
        if len(result) == 0:
            api.item.create(cal_item)
            logging.info(f'{cal_item} creating success')
        else:
            logging.debug(f'{cal_item} already exists')


def create_cpu_aggregation_item(api, host, groups):
    """
    创建主机组cpu平均利用率的Aggregate监控项
    :param api:
    :param host:
    :param groups:
    :return:
    """
    item = {"delay": 60,
            "hostid": "",
            "key_": "",
            "name": '',
            # Zabbix aggregate
            "type": 8,
            # numeric float
            "value_type": 0,
            # decimal
            "data_type": 0,
            # "applications": [app["applicationid"] for app in apps],
            "units": "%"
            }

    item["hostid"] = host["hostid"]
    apps = api.application.get({
        'hostids': host["hostid"], 'filter': {"name": 'CPU aggregation'}
    })
    item["applications"] = [app["applicationid"] for app in apps]
    for grp in groups:
        item["key_"] = "grpavg[\"%s\",\"system.cpu.util[,system]\",last]" % grp
        item["name"] = f'Average cpu utilization in group {grp}'
        result = api.item.get({
            'hostids': host["hostid"], 'filter': {'key_': item["key_"]}
        })
        if len(result) == 0:
            api.item.create(item)
            logging.info(f'{item} creating success')
        else:
            logging.debug(f'{item} already exists')


def main(args):
    zapi = args.zapi
    svr_host = zapi.host.get({
        'filter': {"host": "Zabbix server"}
    })[0]
    create_fs_aggregation_item(api=zapi, host=svr_host, groups=args.hostgroup)
    create_memory_aggregation_item(api=zapi, host=svr_host, groups=args.hostgroup)
    create_cpu_aggregation_item(api=zapi, host=svr_host, groups=args.hostgroup)
