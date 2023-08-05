"""
在各主机上创建总磁盘空间和已用磁盘空间两个监控项。
ZABBIX 3.0版本没有直接获取总磁盘和已用磁盘空间的监控项，只有各挂载的各文件系统的空间使用情况，
因此在各挂载文件系统监控项的基础上创建一个汇总的Calculated监控项
涉及的监控项为 vfs.fs.size[fs,total] vfs.fs.size[fs,used]
创建的计算监控项key为 vfs.fs.totalsize vfs.fs.usedsize
"""
import argparse
import logging


parser = argparse.ArgumentParser()
parser.set_defaults(handler=lambda args: main(args))


APP_NAME = 'Filesystem calculation'

def calculated_formula(items, mode):
    # last("vfs.fs.size[/,total]") + last("vfs.fs.size[/boot,total]")
    filter_keys = ["last(\"" + item["key_"] + "\")" for item in items if mode in item["key_"]]
    formula = '+'.join(filter_keys)
    return formula if formula else "0"


def create_calculated_disk_space_item(api, host, item_name, item_key, params):
    apps = api.application.get({
        'hostids': host["hostid"],
        'filter': {"name": APP_NAME}
    })
    if len(apps) == 0:
        logging.warning("Warning, {0} has no {1} application".format(host['name'], APP_NAME))
    item = {"delay": 3600,
            "hostid": host["hostid"],
            # "interfaceid": [interface["interfaceid"] for interface in host["interfaces"] if interface["type"] == 1],
            "key_": item_key,
            "name": item_name,
            # calculated
            "type": 15,
            # numeric unsigned
            "value_type": 3,
            # decimal
            "data_type": 0,
            "applications": [app["applicationid"] for app in apps],
            "units": "B",
            "params": params
            }

    result = api.item.create(item)
    logging.debug(f"{host['name']} {item['name']} creating success.")
    return result


# def create_aggregate_item(api, hosts, groups, key):
#     agg_item_name = 'Total disk space in $1'
#     agg_item_key = 'grpsum["%s","%s",last]' %

def update_calculated_item_formula(api, items, formula):
    for item in items:
        if item["params"] != formula:
            item["params"] = formula
            api.item.update({
                'itemid': item["itemid"], 
                'params': formula
            })
            logging.info(f"{item} formula is updated.")
        else:
            logging.debug(f"{item} formula is unchanged.")


def upinsert_total_disk_space_item(api, hosts):
    total_item_name = "Total disk space"
    total_item_key = "vfs.fs.totalsize"
    used_item_name = "Used disk space"
    used_item_key = "vfs.fs.usedsize"
    for host in hosts:
        # create_calculated_application(api, host)
        # fs_size_items = api.item.get(hostids=host["hostid"], search={"key_": "vfs.fs.size"})
        fs_size_items = api.item.get({
            'hostids': host["hostid"], 
            'search': {
                "key_": "vfs.fs.size"
                }
        })
        total_formula = calculated_formula(fs_size_items, "total")
        # total_items = api.item.get(hostids=host["hostid"], filter={"name": total_item_name})
        total_items = api.item.get({
            'hostids': host["hostid"], 
            'filter':{
                "name": total_item_name
            }
        })
        if len(total_items) == 0:
            create_calculated_disk_space_item(api, host, total_item_name, total_item_key, total_formula)
        else:
            update_calculated_item_formula(api, total_items, total_formula)

        # used_items = api.item.get(hostids=host["hostid"], filter={"name": used_item_name})
        used_items = api.item.get({
            'hostids': host["hostid"], 
            'filter': {"name": used_item_name}
        })
        used_formula = calculated_formula(fs_size_items, "used")
        if len(used_items) == 0:
            create_calculated_disk_space_item(api, host, used_item_name, used_item_key, used_formula)
        else:
            update_calculated_item_formula(api, used_items, used_formula)


def main(args):
    zapi = args.zapi
    hosts = zapi.host.get({
        'output': ['hostid', 'name'],
        'filter': {
            'available': 1,
            'status': 0
        },
        'searchInventory': {
            'os_short': ['Linux', 'Windows']
        },
        'searchByAny': True
    })
    
    upinsert_total_disk_space_item(zapi, hosts)