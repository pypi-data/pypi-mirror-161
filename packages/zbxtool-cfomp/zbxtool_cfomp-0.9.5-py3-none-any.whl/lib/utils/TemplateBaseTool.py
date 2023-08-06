import logging
from zabbix_api import ZabbixAPIException
import prettytable as pt

class BaseTool:
    """提供模板的公共操作"""
    templates = []

    def __init__(self, args):
        self.zapi = args.zapi
        self.hosts = args.hosts or ['']
        self.groups = args.groups or ['']
        self.gen_hosts_info()
        self.gen_templates_info()

    def get_all_hosts(self) -> None:
        """指定的hosts名称 + 指定的group中的hosts名称"""
        if self.groups:
            groups_info = self.zapi.hostgroup.get({
                'filter': {'name': self.groups},
                'selectHosts': ['host']
            })
            self.hosts += [h['host'] for g in groups_info for h in g['hosts']]

    def gen_hosts_info(self) -> None:
        """获取hosts的信息"""
        self.get_all_hosts()
        self.hosts_info = self.zapi.host.get({
            'output': ['host'],
            'selectParentTemplates': ['host'],
            'filter': {'host': self.hosts}
        })

    def _get_templates_info(self, tpl_names: list) -> list:
        """内部方法, 提供的模板名称, 获取对应的模板信息"""
        return self.zapi.template.get({'filter': {'host': tpl_names}, 'output': ['host']})

    def gen_templates_info(self) -> None:
        """获取参数指定的模板信息"""
        self.templates_info = self._get_templates_info(self.templates)

    def update_host(self, params) -> None:
        """更新host"""
        try:
            self.zapi.host.update(params)
            logging.info('update success! hostid: {}'.format(params['hostid']))
        except ZabbixAPIException as err:
            logging.error(err)

    def pretty_print(self) -> None:
        """表格化打印"""
        tb = pt.PrettyTable()
        tb.title = 'Results of linked templates'
        tb.field_names = ['Host', 'Templates']
        tb.align['Host'] = "l"
        tb.align['Templates'] = "l"

        for h in self.hosts_info:
            tb.add_row([h['host'], ', '.join([t['host'] for t in h['parentTemplates']])])
        print(tb)
