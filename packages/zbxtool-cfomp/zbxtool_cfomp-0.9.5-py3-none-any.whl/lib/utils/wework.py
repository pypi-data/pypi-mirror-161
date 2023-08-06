#!/bin/env python3
# coding:utf-8
"""
    从企业微信中获取用户ID，更新到zabbix用户的企业微信告警媒介的sendto
"""

import sys
import logging
import copy
from zabbix_api import ZabbixAPIException
from weworkapi.CorpApi import CORP_API_TYPE, CorpApi
from weworkapi.AbstractApi import ApiException
import prettytable as pt

# 告警级别
NOT_CLASSIFIED = 1
INFORMATION = 2
WARNING = 4
AVERAGE = 8
HIGH = 16
DISASTER = 32

# wework告警级别
WEWORK_SEVERITY = [WARNING, AVERAGE, HIGH, DISASTER]
# wework告警启用状态，'0'->enabled, '1'->disabled
WEWORK_ACTIVE = '0'
# wework告警启用时间
WEWORK_PERIOD = '1-7,00:00-24:00'

# 告警媒介类型和属性对照, 用来判断sendto是邮箱|手机号码|(企业)微信用户
MediaAttrList = [
   {"kind": "email", "media_type_name": ["Email"], "attr": "email"},
   {"kind": "sms", "media_type_name": ["FortuneSMS"], "attr": "mobile"},
   {"kind": "wework", "media_type_name": ["wework-sendmsg"], "attr": "wework_id"}
]

# 通过手机号码匹配
MATCH_MOBILE = lambda z_user,w_user: w_user['mobile'] in z_user.get('mobile', [])
# 通过姓名 surname + name 匹配
MATCH_NAME = lambda z_user,w_user: z_user['fullname'] == w_user['name']
# 通过姓名 name + surname 匹配
MATCH_REVERSE_NAME = lambda z_user,w_user: z_user['fullname_reverse'] == w_user['name']
# 通过邮箱匹配
MATCH_EMAIL = lambda z_user,w_user: w_user['email'] in z_user.get('email', [])

# 匹配函数列表, 列表中的方法依次执行, 直到表达式返回True
MATCH_FUNCS = [MATCH_MOBILE, MATCH_NAME, MATCH_REVERSE_NAME, MATCH_EMAIL]



class SyncWeworkMedia:
    """
       1.从zabbix用户告警媒介中，通过报警媒介类型, 提取到用户的手机号码、邮箱、姓名等信息.
       2.通过多种途径匹配到该用户在企业微信的userid.
       3.优先通过手机号码匹配, 如用户无手机号码或手机号码匹配不到，再依次通过其他途径匹配.
       4.最终匹配到企业微信的userid的用户, 新建或更新报警媒介.
    """

    def __init__(self, zapi, corpapi, depart_name=None,
                 zbx_usrgrps=None, zbx_username='',
                 allow_update=False):
        self._zapi = zapi
        self._corpapi = corpapi
        self._usrgrps = zbx_usrgrps
        self._depart_name = depart_name
        self._username = zbx_username
        self._allow_update = allow_update
        self.set_default()


    def set_default(self):
        """
            初始化运行所需参数
        """
        self.media_attr = {}
        self.wework_media_type_ids = []
        self.wework_severity = sum(WEWORK_SEVERITY)
        self.wework_active = WEWORK_ACTIVE
        self.wework_period = WEWORK_PERIOD
        self.match_funcs = MATCH_FUNCS


    def run(self):
        """
            执行同步
        """
        self.set_media_attr()
        self.get_zbx_users()
        self.get_wework_users()
        for z_u in self.zbx_users:
            self.add_user_media_wework(z_u, update=self._allow_update)


    def get_wework_users(self):
        """
            获取企业微信中，指定部门的用户信息, 保存至self.wework_users
        """
        # 从企业微信部门列表中找到指定部门->target_depart
        departs = self._wework_request(CORP_API_TYPE['DEPARTMENT_LIST'])
        target_depart = [d['id'] for d in departs['department'] if d['name'] == self._depart_name]

        if target_depart:
            depart_id = str(target_depart[0])
        else:
            logging.error(f'企业微信中未找到部门:{self._depart_name}.')
            sys.exit(1)

        # 获取该部门下所有人员, 包含子部门的人员
        response = self._wework_request(CORP_API_TYPE['USER_LIST'], {
            'department_id': depart_id,
            'fetch_child': '1'
        })
        self.wework_users = response['userlist']


    def match_wework_userid(self, zbx_user):
        """
            匹配zabbix用户对应的企业微信userid
            依次执行 match_funcs 列表中的匹配方法, 直到表达式返回True停止
            返回对应的userid
        """
        for match_func in self.match_funcs:
            result = [u for u in self.wework_users if match_func(zbx_user, u)]
            if result:
                return result[0]['userid']
        return None


    def get_zbx_users(self):
        """
            获取zabbix中用户相关信息
            根据用户告警媒介获取对应的手机号、邮箱、完整姓名、完整姓名反转等属性
        """

        # 获取指定zabbix用户组的groupid
        gids = [g['usrgrpid'] for g in self.get_zbx_usergroup()]

        # 获取指定groupid/全部的zabbix用户, gids为空列表时, 会返回全部zabbix用户
        params = {
            "output": ["alias", "name", "surname"],
            "usrgrpids": gids,
            "selectMedias": ["mediatypeid", "sendto", "active", "severity", "period"],
            "filter": {"alias": self._username}
        }
        self.zbx_users = self._zbx_request('user.get', params)

        # 根据zabbix用户所具有的media, 为用户添加(mobile|email)等属性, 方便进行匹配
        for zbx_user in self.zbx_users:
            # 添加fullname 和 fullname_reverse，即姓+名 和 名+姓
            zbx_user['fullname'] = zbx_user.get('surname','') + zbx_user.get('name','')
            zbx_user['fullname_reverse'] = zbx_user.get('name','') + zbx_user.get('surname','')

            for media in zbx_user['medias']:
                if media['mediatypeid'] in self.media_attr:
                    attr = self.media_attr[media['mediatypeid']]
                    sendto = media['sendto'] if isinstance(media['sendto'], list) else [media['sendto']]
                    if zbx_user.get(attr):
                        zbx_user[attr] += sendto
                    else:
                        zbx_user[attr] = sendto
                else:
                    continue


    def set_media_attr(self):
        """
            设置 告警媒介类型 与 用户属性(手机号|邮箱|wework_id) 的对应关系
        """
        mts = self._zbx_request('mediatype.get', {
            "output": ["description"]
        })
        # 遍历zabbix所有媒介类型, 根据对照关系, 判断是那种属性(mobile|email|wework_id)
        # 当zabbux用户具有该类型的媒介时, 则用户应具有对应的属性
        for mt in mts:
            for item in MediaAttrList:
                if mt['description'] in item['media_type_name']:
                    self.media_attr[mt['mediatypeid']] = item['attr']
                    # 如果媒介类型是属于企业微信的, 则保存至wework_media_type_ids
                    if item['kind'] == 'wework':
                        self.wework_media_type_ids.append(mt['mediatypeid'])
                    break


    def get_zbx_usergroup(self):
        """
            获取zabbix中用户组名称对应groupid
        """
        return self._zbx_request('usergroup.get', {
            "output": ["name"],
            "filter": {
                "name": self._usrgrps
            }
        })


    def add_user_media_wework(self, zbx_user, update=False):
        """
            为zabbix用户添加企业微信告警媒介。

            update: 如用户已经存在企业微信告警媒介, 且原userid与获取到的userid不一致,
                    值为False 则不做处理，
                    值为True 则更新为获取到的userid。
        """
        wework_userid = self.match_wework_userid(zbx_user)
        if not wework_userid:
            logging.info(f"同步失败: zabbix user {zbx_user['alias']} 未找到对应的企业微信账号.")
            return

        zbx_user_medias = zbx_user['medias']
        zbx_user_medias_copy = copy.deepcopy(zbx_user['medias'])

        for typeid in self.wework_media_type_ids:
            # zabbix user 已经有wework报警媒介
            origin_wework_media = [m for m in zbx_user_medias if m['mediatypeid'] == typeid]
            if origin_wework_media:
                # update为True 则更新为获取到的userid
                [m.update({'sendto': wework_userid}) for m in origin_wework_media if update]
            else:
                # 添加wework报警媒介
                zbx_user_medias.append({
                    'mediatypeid': typeid,
                    'sendto': wework_userid,
                    'active': self.wework_active,
                    'severity': self.wework_severity,
                    'period': self.wework_period
                })

        # 如果zabbix user的media有被修改过, 则进行更新
        if zbx_user_medias != zbx_user_medias_copy:
            self._zbx_request('user.update', {
                'userid': zbx_user['userid'],
                'user_medias': zbx_user['medias']
            })
            zbx_user['wework_id'] = [wework_userid]
            logging.info(f"同步成功: zbx_user:{zbx_user['alias']} wework_userid:{wework_userid}")


    def _zbx_request(self, method, params):
        """
            封装对zapi的调用
        """
        try:
            module, func = method.split('.')
            return getattr(getattr(self._zapi, module), func)(params)
        except ZabbixAPIException as err:
            logging.error(err)
            sys.exit(1)


    def _wework_request(self, api_type, params=None):
        """
            封装对corpapi的调用
        """
        try:
            return self._corpapi.httpCall(api_type, params)
        except ApiException as err:
            logging.error(err)
            sys.exit(1)


    def show(self):
        """表格化打印"""
        table = pt.PrettyTable()
        table.title = 'Zabbix用户企业微信账号对照'
        table.field_names = ['Zabbix User', 'Full Name', 'Wework UserId']
        table.align['Zabbix User'] = "l"
        table.align['Full Name'] = "l"
        table.align['Wework UserId'] = "l"

        for zbx_user in self.zbx_users:
            table.add_row([zbx_user['alias'], zbx_user['fullname'], zbx_user.get('wework_id', [])])
        print(table)


    @staticmethod
    def create_corpapi(corpid:str, secret:str, token:str=None) ->CorpApi:
        """
            创建企业微信api实例
        """
        corpapi = CorpApi(corpid, secret)
        corpapi.access_token = token
        return corpapi

