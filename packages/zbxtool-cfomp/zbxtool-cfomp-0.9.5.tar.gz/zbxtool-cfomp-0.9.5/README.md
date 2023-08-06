# zbxtool

提供一些修改zabbix的操作。

## 使用
```shell
# python setup.py install

usage: zbxtool [-h] -s ZBX_SERVER -u ZBX_USER -p ZBX_PASSWD [-t TIMEOUT] [-v]
               [command] ...

optional arguments:
  -h, --help            show this help message and exit
  -s ZBX_SERVER, --zbx-server ZBX_SERVER
                        URL of zabbix server
  -u ZBX_USER, --zbx-user ZBX_USER
                        Zabbix server login username
  -p ZBX_PASSWD, --zbx-passwd ZBX_PASSWD
                        Zabbix server login password
  -t TIMEOUT, --timeout TIMEOUT
                        Zabbix API timeout
  -v, --verbose         Print debug information

subcommands:

  [command]
    discovery
    es_index_zbxhost
    multi_interfaces 
    service_tree
    update_hostgrp_poc
    update_hostname
    vmware_host_inventory
    oob
    ldap_usergrp
    inventory_supplementary
    sync_wework_media
```

### 子命令说明

- **discovery**: 打印Zabbix自动发现的host, 并输出到excel.

- **vmware_host_inventory**: 通过Api读取vCenter信息，更新 Zabbix 中 Hypervisors 组中Host的 inventory 信息。

- **update_hostgrp_poc**: 读取ldap人员信息, 更新 Zabbix 中各组主机的 inventory。

- **update_hostname**: 消除 Zabbix 中 Discovered Hosts 组中hostname 末尾的下划线+数字的情况。

- **service_tree**: 在 Zabbix 中 依据主机组生成it-service树

- **es_index_zbxhost**: 将 Zabbix 中各主机的inventory信息采集至ElasticSearch的Index中

- **multi_interfaces**: 输出 Zabbix 各主机的inventory的Host networks字段中的ip信息

- **oob**: 更新主机的inventory OOB IP address字段

- **ldap_usergrp**: 创建zabbix每个主机组的用户组, 并同步到ldap的ou=zabbix的user groups中

- **inventory_supplementary**: vmware主机更新inventory type字段为vm, 主机有rsync进程监控项更新inventory tag字段.

- **sync_wework_media**: 从企业微信中获取用户ID，更新到zabbix用户的企业微信告警媒介的sendto

### 示例
- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password update_hostname

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password vmware_host_inventory

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password vmware_host_inventory -l 10.189.61.62 10.189.61.63 -l 10.189.61.64

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password service_tree delete --service-name test

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password service_tree create --service-name test --group-name Orabbix

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password es_index_zbxhost --es_url 10.189.67.26 [--es_user] [--es_passwd]

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password update_hostgrp_poc -c Contacts.json --ldap-server 10.189.67.14 --ldap-user cn=Manager,dc=shchinafortune,dc=local --ldap-password password

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password discovery --drule 750-开发* -o result.xlsx

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password multi_interfaces -o result.xlsx

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password oob

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password ldap_usergrp --ldap-server 10.189.67.14 --ldap-user cn=Manager,dc=shchinafortune,dc=local --ldap-password xxxx --create-ldap-group --create-zbx-usrgrp

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password inventory_supplementary

- zbxtool -s http://10.189.67.39/zabbix -u liusong -p password sync_wework_media  --corpid corpid --secret secret -d '华鑫运管平台-测试' -t /tmp/token-cache -g  "Zabbix administrators"

