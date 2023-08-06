"""
提供模板的显示、添加、清除、替换等操作
"""
from .TemplateBaseTool import BaseTool

class ListTemplate(BaseTool):
    """仅提供格式化输出功能"""
    def __init__(self, args):
        super(ListTemplate, self).__init__(args)
        self.pretty_print()


class AddTemplate(BaseTool):
    """提供添加模板的功能"""
    def __init__(self, args):
        self.templates = args.add
        super(AddTemplate, self).__init__(args)
        self.add()

    def add(self) -> None:
        for h in self.hosts_info:
            params = {'hostid': h['hostid'], 'templates': self.templates_info + h['parentTemplates']}
            self.update_host(params)
        # 打印更新结果
        self.gen_hosts_info()
        self.pretty_print()


class ClearTemplate(BaseTool):
    """移除指定模板"""
    def __init__(self, args):
        self.templates = args.clear
        super(ClearTemplate, self).__init__(args)
        self.clear()

    def clear(self) -> None:
        for h in self.hosts_info:
            params = {'hostid': h['hostid'], 'templates_clear': self.templates_info}
            self.update_host(params)
        # 打印更新结果
        self.gen_hosts_info()
        self.pretty_print()


class UseTemplate(BaseTool):
    """替换掉全部模板"""
    def __init__(self, args):
        self.templates = args.use
        super(UseTemplate, self).__init__(args)
        self.use()

    def use(self) -> None:
        for h in self.hosts_info:
            params = {'hostid': h['hostid'], 'templates': self.templates_info}
            self.update_host(params)
        # 打印更新结果
        self.gen_hosts_info()
        self.pretty_print()


class ReplaceTemplate(BaseTool):
    """替换掉指定模板"""
    def __init__(self, args):
        self.templates = args.replace
        self.instead_templates = args.to
        super(ReplaceTemplate, self).__init__(args)
        self.replace()

    def replace(self) -> None:
        # 替换后的templates
        instead_templates_info = self._get_templates_info(self.instead_templates)
        for h in self.hosts_info:
            # 过滤掉被替换的templates
            new_templates = list(filter(lambda t: t not in self.templates_info, h['parentTemplates']))
            new_templates += instead_templates_info
            params = {'hostid': h['hostid'], 'templates': new_templates}
            self.update_host(params)
        # 打印更新结果
        self.gen_hosts_info()
        self.pretty_print()


