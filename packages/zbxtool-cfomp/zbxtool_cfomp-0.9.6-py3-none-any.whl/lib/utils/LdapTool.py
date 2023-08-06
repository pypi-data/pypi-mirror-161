"""
提供ldap常用的操作
目前支持查找用户, 清除用户组, 创建用户组, 修改用户组成员
"""
import logging
import ldap3
import functools

class Ldap:
    """ldap usergroup 删除、添加、更新"""
    def __init__(self, host, user, passwd, port=389):
        self.logged_in = False
        self.login(ldap3.Server(host, port), user, passwd)

    def login(self, ldap_server, user, passwd):
        """登录"""
        try:
            self._conn = ldap3.Connection(ldap_server, user, passwd, auto_bind=True)
            self.logged_in = True
        except Exception as err:
            logging.error(err)

    def check_login(fun):
        """类内装饰器 检查ldap是否已登录"""
        @functools.wraps(fun)
        def _fun(self, *args, **kwargs):
            if self.logged_in:
                return fun(self, *args, **kwargs)
            else:
                logging.error('no login')
        return _fun

    @check_login
    def search_user(self, dn, user) -> str:
        """查询并返回用户信息"""
        res = self._conn.search(
            search_base = dn,
            search_scope = ldap3.SUBTREE,
            search_filter = '(uid={})'.format(user),
            attributes = ldap3.ALL_ATTRIBUTES
        )
        return self._conn.response[0]['raw_dn'] if res else None

    @check_login
    def search_usergrp(self, dn, usergrp='*') -> list:
        """查询并返回用户组信息"""
        res = self._conn.search(
            search_base = dn,
            search_scope = ldap3.SUBTREE,
            search_filter = '(cn={})'.format(usergrp),
            attributes = ldap3.NO_ATTRIBUTES
        )
        return [g['dn'] for g in self._conn.response]


    @check_login
    def clean_usergrp(self, dn) -> None:
        """清除用户组"""
        for usergrp in self.search_usergrp(dn):
            try:
                self._conn.delete(usergrp)
            except Exception as err:
                logging.error(err)

    @check_login
    def create_usergrp(self, dn, member:list=None) -> None:
        """创建用户组, 添加组成员"""
        try:
            self._conn.add(dn, 'groupOfUniqueNames')
            if member:
                self.update_member(dn, member)
        except Exception as err:
            logging.error(err)

    @check_login
    def update_member(self, cn, member:list=None) -> None:
        if not member:
            member = []
        try:
            self._conn.modify(cn, {'uniqueMember': [(ldap3.MODIFY_REPLACE, member)]})
        except Exception as err:
            logging.error(err)
