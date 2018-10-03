# coding: UTF-8

import yaml
from zabbix_api import ZabbixAPI
from lib import zabbix
from lib.helper import logger

yaml_path = 'config.yml'

def main():
    """delete_zabbix_hosts
    config.yml に登録されている Default Groups に登録されているHost全てを削除する。
    """
    with open(yaml_path) as f:
        config = yaml.load(f)

    zapi = ZabbixAPI(server=config['zabbix']['server'])
    logger.info("Zabbix login: %s" % config['zabbix']['server'])
    zapi.login(config['zabbix']['username'], config['zabbix']['password'])

    groups = [zabbix.HostGroup(zapi, g) for g in config['general']['default_groups']]

    groupids = [g['groupid'] for g in groups]
    params = {'groupids': groupids}
    res = zapi.host.get(params)
    hostids = [h['hostid'] for h in res]

    if hostids:
        logger.info("Delete %s Hosts." % len(hostids))
        zapi.host.delete(hostids)

if __name__ == '__main__':
    main()
