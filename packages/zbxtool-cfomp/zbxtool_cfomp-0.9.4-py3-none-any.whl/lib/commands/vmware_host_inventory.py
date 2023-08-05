#!/bin/env python3
# coding:utf-8

"""
从vCenter中获取esxi主机信息，更新到Zabbix inventory
"""
import sys
import argparse
import logging
from urllib.parse import urlparse
from pyVmomi import vim, vmodl
from pyVim.connect import Disconnect, SmartConnectNoSSL
from infi.pyvmomi_wrapper.esxcli import EsxCLI
from zabbix_api import ZabbixAPIException
from lib.utils.inventory_tag import InventoryTagDict

parser = argparse.ArgumentParser("Correct discoverd host name")
parser.add_argument('-l', '--limit', action='append', type=str, help="Specify hypervisors")
parser.set_defaults(handler=lambda args: main(args))


def fetch_esxi(host, user, pwd, esxi_name, port=443):
    '''
    通过 pyVmomi 模块读取 vCenter 中 esxi server的信息。
    '''
    si = SmartConnectNoSSL(host=host, user=user, pwd=pwd, port=port)
    content = si.RetrieveContent()
    container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem, vim.Datacenter], True)

    # vcenter自定义的属性, 取系统中对应的字段的key, {'机柜': 43, '机房名称': 44}
    custom_key = {'机柜':'', '机房名称':''}

    cfm = content.customFieldsManager
    for field in cfm.field:
        if field.name in custom_key.keys():
            custom_key[field.name] = field.key

    esxi_info = {}

    # 取数据中心的机房名称
    for view in container.view:
        if not isinstance(view, vim.Datacenter):
            continue

        # esxi 属于某 datacenter, 则取 datacenter 自定义属性
        for child in view.hostFolder.childEntity:

            isFind = False  #是否在该 datacenter 找到目标 esxi

            # 子节点是 ClusterCompute, esxi 挂在 ClusterCompute下面
            if isinstance(child, vim.ClusterComputeResource):
                for host in child.host:
                    if esxi_name == host.name:
                        isFind = True
            else:
            # esxi 直接挂在 datacenter 下
                if esxi_name == child.name:
                    isFind = True

            if isFind:
                # location 默认值为datacenter的名字
                esxi_info['location'] = view.name
                # 如果datacenter有“机房名称”自定义属性，则覆盖前者。
                for prop in view.customValue:
                    if prop.key == custom_key['机房名称']:
                        esxi_info['location'] = prop.value
                        break


    # 取esxi属性
    for esxi_ in container.view:
        if esxi_.name != esxi_name:
            continue
        cpu = '(%s) * %s  %s核  %s线程' % (esxi_.summary.hardware.cpuModel,
                           esxi_.summary.hardware.numCpuPkgs,
                           esxi_.summary.hardware.numCpuCores,
                           esxi_.summary.hardware.numCpuThreads)
        mem = f'内存: {esxi_.summary.hardware.memorySize/1024/1024//1024}GB'
        esxi_info['type'] = 'Server'
        esxi_info['name'] = esxi_.name
        esxi_info['os'] = esxi_.config.product.name
        esxi_info['os_full'] = esxi_.summary.config.product.fullName
        esxi_info['os_short'] = esxi_.config.product.osType
        esxi_info['model'] = esxi_.summary.hardware.model
        esxi_info['vendor'] = esxi_.summary.hardware.vendor
        #esxi_info['management_ip'] = esxi_.summary.managementServerIp
        esxi_info['hardware_full'] = '\n'.join([cpu, mem])

        # get host's ipA and netmask
        for vnic in esxi_.config.network.vnic:
            if isinstance(vnic, vim.host.VirtualNic):
                esxi_info['host_networks'] = vnic.spec.ip.ipAddress
                esxi_info['alias'] = vnic.spec.ip.ipAddress
                esxi_info['host_netmask'] = vnic.spec.ip.subnetMask

        # get host's mac address
        for portgroup in esxi_.config.network.portgroup:
            for port in portgroup.port:
                if port.type == 'host':
                    esxi_info['macaddress_a'] = ''.join(port.mac)

        # get host's serial_number
        ordered_keys = ['SerialNumberTag', 'EnclosureSerialNumberTag', 'ServiceTag']
        sn_info = {}
        for iden in esxi_.summary.hardware.otherIdentifyingInfo:
            if isinstance(iden, vim.host.SystemIdentificationInfo) and iden.identifierType.key in ordered_keys:
                sn_info[iden.identifierType.key] = iden.identifierValue

        for key in ordered_keys:
            if sn_info.get(key):
                esxi_info['serialno_a'] = sn_info.get(key)
                break

        if not esxi_info.get('serialno_a'):
            cli = EsxCLI(esxi_)
            hardware = cli.get("hardware.platform")
            esxi_info['serialno_a'] = hardware.Get().SerialNumber


        # 取机柜名称
        esxi_info['site_rack'] = None
        for prop in esxi_.customValue:
            if prop.key == custom_key['机柜']:
                esxi_info['site_rack'] = prop.value
                break

    Disconnect(si)
    return esxi_info


def main(args):
    '''
    更新 zabbix 中 Hypervisors 组中 host 的 inventory. 其内容从 vCenter 中获取.
    '''
    zapi = args.zapi

    zbx_group = zapi.hostgroup.get({
        'output': ['groupid', 'name'],
        'selectHosts': ['hostid', 'name'],
        'filter': {'name': 'Hypervisors'}
    })

    if not zbx_group:
        sys.exit()

    grp_hosts = zbx_group[0].get('hosts')

    # 如指定limit参数, 则仅处理列表中的host
    if args.limit:
        grp_hosts = [h for h in grp_hosts if h['name'] in args.limit]


    # 调用zapi 查询host的macros信息
    hosts = zapi.host.get({
        'output': ['hostid', 'name'],
        'hostids': [h['hostid'] for h in grp_hosts],
        'selectMacros': ['macro', 'value'],
        'selectInventory': 'extend'
    })

    for host in hosts:
        host_id = host['hostid']
        host_name = host['name']
        tags = InventoryTagDict(host['inventory']['tag'])
        tags['Esxi'] = None

        # 从zabbix host的macros 中取出对应的vcenter登录信息
        url = ''.join([ma['value'] for ma in host['macros'] if ma['macro'] == '{$URL}'])
        vcenter_ip = urlparse(url).hostname
        vcenter_admin = ''.join([ma['value'] for ma in host['macros'] if ma['macro'] == '{$USERNAME}'])
        vcenter_pwd = ''.join([ma['value'] for ma in host['macros'] if ma['macro'] == '{$PASSWORD}'])

        try:
            logging.info(f'[fetch_esxi] vcenter_ip: {vcenter_ip}, esxi_name:{host_name}')
            esxi_info = fetch_esxi(host=vcenter_ip,
                                   user=vcenter_admin,
                                   pwd=vcenter_pwd,
                                   esxi_name=host_name)
 
            esxi_info.update({'tag': str(tags)})
            update_params = {'hostid': host_id, 'inventory': esxi_info}
            if host['inventory']['inventory_mode'] == '-1':  # disabled
                update_params['inventory_mode'] = '1'  # Auto
            zapi.host.update(update_params)
            logging.info(f'update host->{host_name} success!')

        except ZabbixAPIException as error:
            logging.exception(error)
        except vmodl.MethodFault as error:
            logging.exception(error.msg)
            continue
