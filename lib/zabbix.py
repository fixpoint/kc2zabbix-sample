# coding: UTF-8

from pprint import pprint
from collections import OrderedDict
from collections import defaultdict

class HostInterface(object):

    def __init__(self):
        self.zapi = zapi
        self.info = None

class HostGroup(object):

    def __init__(self, zapi, name_or_id):
        self.zapi = zapi
        self.info = None

        self.name = name_or_id
        self.id = None
        if isinstance(name_or_id, int):
            self.name, self.id = self.id, self.name

    def get(self, key):
        if self.info is None:
            if self.id:
                params = {"filter": {"groupid": [self.id]}}
            else:
                params = {"filter": {"name": [self.name]}}
            res = self.zapi.hostgroup.get(params)
            if res:
                self.info = res[0]
                self.name = self.info.get('name')
                self.id = self.info.get('groupid')
            else:
                self.info = {}

        return self.info.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def save(self):
        if self['groupid']:
            result = self.zapi.hostgroup.update({"name": self.name, "groupid": self.id})
        else:
            result = self.zapi.hostgroup.create({"name": self.name})
        self.info = None
        return result["groupids"][0]

class Template(object):

    def __init__(self, zapi, name_or_id):
        self.zapi = zapi
        self.info = None
        self.parent_templates = set()
        self.child_templates = set()

        self.host = name_or_id
        self.id = None
        if isinstance(name_or_id, int):
            self.host, self.id = self.id, self.host

    def get(self, key):
        if self.info is None:
            params = {}
            if self.id:
                params.update({"filter": {"templateid": [self.id]}})
            else:
                params.update({"filter": {"host": [self.host]}})
            res = self.zapi.template.get(params)
            if res:
                self.info = res[0]
                self.host = self.info.get('host')
                self.id = self.info.get('templateid')
                self._make_parent_templates(self.host)
                self._make_child_templates(self.host)
            else:
                self.info = {}

        return self.info.get(key)
    
    def in_parent(self, template):
        if not self['host']: return False
        return (template in self.parent_templates)
    
    def in_child(self, template):
        if not self['host']: return False
        return (template in self.child_templates)
    
    def _make_parent_templates(self, template):
        tmplates = self._get_templates()
        for p_tmpl in tmplates[template]['parentTemplates']:
            self.parent_templates.add(p_tmpl['host'])
            self._make_parent_templates(p_tmpl['host'])

    def _make_child_templates(self, template):
        tmplates = self._get_templates()
        for p_tmpl in tmplates[template]['templates']:
            self.child_templates.add(p_tmpl['host'])
            self._make_child_templates(p_tmpl['host'])

    def _get_templates(self):
        if 't_templates' not in self.__dict__:
            params = {
                "output": ["templateid", "host"],
                "selectTemplates": ["templateid", "host"],
                "selectParentTemplates": ["templateid", "host"],
            }
            res = self.zapi.template.get(params)
            self.t_templates = {v['host']: v for v in res}
        return self.t_templates

    def __getitem__(self, key):
        return self.get(key)
    
    def __repr__(self):
        return "<zabbix.Template: {0}>".format(self.host or self.id)

class Host(object):

    def __init__(self, zapi, name_or_id):
        self.zapi = zapi
        self.info = None
        self.new_info = {}
        self.interfaces = defaultdict(lambda: OrderedDict())
        self.groups = []
        self.templates = []
        self.inventory = {}

        self.host = name_or_id
        self.id = None
        if isinstance(name_or_id, int):
            self.host, self.id = self.id, self.host

    def get(self, key):
        if self.info is None:
            params = {"selectInterfaces": "extend"}
            if self.id:
                params.update({"filter": {"hostid": [self.id]}})
            else:
                params.update({"filter": {"host": [self.host]}})
            res = self.zapi.host.get(params)
            if res:
                self.info = res[0]
                self.host = self.info.get('host')
                self.id = self.info.get('hostid')
            else:
                self.info = {}
        return self.info.get(key)

    def __getitem__(self, key):
        return self.new_info.get(key) or self.get(key)

    def __setitem__(self, key, value):
        self.new_info[key] = value

    def add_group(self, group):
        if isinstance(group, str):
            group = HostGroup(self.zapi, group)
        self.groups.append(group)

    def add_template(self, template):
        if isinstance(template, str):
            template = Template(self.zapi, template)
        self.templates.append(template)

    def add_interface_agent(self, ip, port=10050):
        self._add_interface({"type": 1, "useip": 1, "ip": ip, "dns": "", "port": str(port)})

    def add_interface_snmp(self, ip, port=161):
        self._add_interface({"type": 2, "useip": 1, "ip": ip, "dns": "", "port": str(port)})

    def _add_interface(self, params):
        key = "{ip}:{port}".format(**params)
        params["main"] = 0 if self.interfaces[params['type']] else 1
        self.interfaces[params['type']][key] = params

    def save(self):
        params = {"host": self.host}
        params.update(self.new_info)
        if 'name' not in params and self['name']:
            params['name'] = self['name']
        if self.groups:
            params["groups"] = [{"groupid": g['groupid']} for g in self.groups]
        if self.templates:
            params["templates"] = [{"templateid": t['templateid']} for t in self.templates]
        if self.inventory:
            params["inventory_mode"] = 0
            params["inventory"] = self.inventory

        if self['hostid']:
            params['hostid'] = self.id
            result = self.zapi.host.update(params)

            interfaces = [iface for t_ifaces in self.interfaces.values() for iface in t_ifaces.values()]
            del_interfaces = []
            for iface in self['interfaces']:
                if interfaces:
                    new_iface = interfaces.pop(0)
                    new_iface['interfaceid'] = iface['interfaceid']
                    self.zapi.hostinterface.update(new_iface)
                else:
                    del_interfaces.append(iface['interfaceid'])
            if interfaces:
                self.zapi.hostinterface.massadd({"hosts": [{"hostid": self.id}], "interfaces": interfaces})
            if del_interfaces:
                self.zapi.hostinterface.delete(del_interfaces)

        else:
            if self.interfaces:
                params["interfaces"] = [iface for t_ifaces in self.interfaces.values() for iface in t_ifaces.values()]
            result = self.zapi.host.create(params)
        self.info = None
        self.new_info = {}
        return result["hostids"][0]

class Map(object):

    def __init__(self, zapi, name_or_id):
        self.zapi = zapi
        self.info = None
        self.new_info = {}

        self.name = name_or_id
        self.id = None
        if isinstance(name_or_id, int):
            self.name, self.id = self.id, self.name

    def get(self, key):
        if self.info is None:
            params = {
                "output": "extend",
                "selectSelements": "extend",
                "selectLinks": "extend",
            }
            if self.id:
                params["filter"] = {"sysmapid": [self.id]}
            else:
                params["filter"] = {"name": [self.name]}
            res = self.zapi.map.get(params)
            if res:
                self.info = res[0]
                self.name = self.info.get('name')
                self.id = self.info.get('sysmapid')
            else:
                self.info = {}

        return self.info.get(key)

    def __getitem__(self, key):
        return self.new_info.get(key) or self.get(key)

    def __setitem__(self, key, value):
        self.new_info[key] = value

    def add_selement(self, elm):
        pass

    def add_link(self, elm_id):
        pass

    def create(self, width, height):
        pass
