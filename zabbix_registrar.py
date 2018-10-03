# coding: UTF-8

import yaml
import argparse
import re

from pprint import pprint
from zabbix_api import ZabbixAPI
from zabbix_api import ZabbixAPIException
from lib import helper
from lib import zabbix
from lib.helper import logger
from lib.kompira_cloud import KompiraCloudAPI

yaml_path = 'config.yml'

def check_duplicate_vname(zapi, name):
    params = {
        "searchWildcardsEnabled": True,
        "search": {"name": name + '*'},
        "output": ["name"]
    }
    result = zapi.host.get(params)
    names = [r["name"] for r in result]
    i = 0
    t_name = name
    while t_name in names:
        t_name = "%s-%d" % (name, i)
        i += 1
    return t_name

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("nodelist_url", type=str)
    args = parser.parse_args()

    with open(yaml_path) as f:
        config = yaml.load(f)

    if config['kompira_cloud'].get('basic_auth'):
        kcapi = KompiraCloudAPI(
            config['kompira_cloud']['token'],
            username=config['kompira_cloud']['basic_auth']['username'],
            password=config['kompira_cloud']['basic_auth']['password'],
        )
    else:
        kcapi = KompiraCloudAPI(config['kompira_cloud']['token'])

    logger.info("Get node list from KompiraCloud")
    res_json = kcapi.get_from_url(args.nodelist_url, {'limit': 500})
    items = res_json['items']

    zapi = ZabbixAPI(server=config['zabbix']['server'])
    logger.info("Zabbix login: %s" % config['zabbix']['server'])
    zapi.login(config['zabbix']['username'], config['zabbix']['password'])

    groups = [zabbix.HostGroup(zapi, g) for g in config['general']['default_groups']]
    for group in groups:
        if not group['groupid']:
            logger.info("Create HostGroup: %s" % group.name)
            group.save()

    base_templates = [zabbix.Template(zapi, t) for t in config['general']['default_templates']]
    snmp_templates = [zabbix.Template(zapi, t) for t in config['general']['snmp_templates']]
    # SNMPテンプレートがデフォルトテンプレートのリンク元に含まれているのであれば削除する
    for s_tmpl in snmp_templates:
        if any(b_tmpl.in_parent(s_tmpl['host']) for b_tmpl in base_templates):
            snmp_templates.remove(s_tmpl)
    # デフォルトテンプレートがSNMPテンプレートのリンク元に含まれていないのであれば追加する
    for b_tmpl in base_templates:
        if not any(s_tmpl.in_parent(b_tmpl['host']) for s_tmpl in snmp_templates):
            snmp_templates.append(b_tmpl)

    for item in items:
        ip = helper.dig(item, 'addresses', 0, 'addr')
        if not ip: continue

        node_id = item.get("managedNodeId") or item.get("nodeId")
        if item.get("managedNodeId"):
            host = config['general']['host_prefix'] + node_id
        else:
            host = config['general']['host_prefix'] + ip

        zh = zabbix.Host(zapi, host)
        zh.groups = groups
        zh.templates = base_templates

        for addr in (item.get('addresses') or []):
            if not addr: continue
            zh.add_interface_snmp(addr['addr'])
            # Check snmp service
            if any(s['name'] == 'snmp' for s in addr['services']):
                zh.templates = snmp_templates

        os_s = helper.dig(item, 'system', 'family')
        os_v = helper.dig(item, 'system', 'version')
        name = helper.dig(item, 'displayName') or \
               helper.dig(item, 'addresses', 0, 'hostnames', 0, 'hostname') or ip

        # Make inventory
        zh.inventory = {
            'type': helper.dig(item, 'deviceTypes', 0, 'type'),
            'name': name,
            'os': os_s,
            'os_full': os_s + ' / ' + os_v if os_v else '',
            'serialno_a': helper.dig(item, 'system', 'serial'),
            'serialno_b': helper.dig(item, 'extraFields', 'product', 'serialNumber'),
            'macaddress_a': helper.dig(item, 'addresses', 0, 'macaddr'),
            'macaddress_b': helper.dig(item, 'addresses', 1, 'macaddr'),
            'hardware': helper.dig(item, 'extraFields', 'product', 'modelName'),
            'hardware_full': yaml.dump(helper.dig(item, 'extraFields'), default_flow_style=False, width=200),
            'model': helper.dig(item, 'extraFields', 'product', 'modelNumber'),
            'url_a': args.nodelist_url + "/" + node_id,
            'vendor': helper.dig(item, 'extraFields', 'product', 'vendorName') or
                      helper.dig(item, 'addresses', 0, 'extraFields', 'macaddr', 'organizationName'),
        }

        # Get packages
        packages_url = "%s/%s/packages" % (args.nodelist_url, node_id)
        packages = kcapi.get_from_url(packages_url, {'limit': 30})
        packages = ["%s (%s)" % (p['name'], p['version']) if p['version'] else p['name']
                    for p in packages['items']]
        if packages:
            header = ["Package list (Top 30):", ""]
            zh.inventory['software'] = "All package list: " + packages_url
            zh.inventory['software_full'] = "\n".join(header + packages)

        new_vname   = config['general']['host_prefix'] + name
        exist_vname = re.sub("-\d$", "", (zh['name'] or ''))

        if zh['hostid']:
            if new_vname != exist_vname:
                zh['name'] = check_duplicate_vname(zapi, new_vname)
            logger.info("Update Host: %s" % zh['name'])
        else:
            zh['name'] = check_duplicate_vname(zapi, new_vname)
            logger.info("Create Host: %s" % zh['name'])

        try:
            zh.save()
        except ZabbixAPIException as e:
            logger.error(e)

if __name__ == '__main__':
    main()
