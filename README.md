# kc2zabbix-sample
Import Nodes data to Zabbix Hosts from Kompira cloud

## Requirements
- Zabbix 3.4
- Python 3.6.5


## Installation

### Install Python

- [Ubuntu](http://ubuntuhandbook.org/index.php/2017/07/install-python-3-6-1-in-ubuntu-16-04-lts/)
- [Windows](https://docs.python.org/3.6/using/windows.html)

### Install Python modules
```
pip install zabbix-api requests PyYAML
```

### Make config.yml

Rename `config.yml.sample` to `config.yml`

```
cp config.yml.sample config.yml
vi config.yml
```

```
# config.yml
zabbix:
  server: http://your.zabbix.server/zabbix
  username: Admin
  password: zabbix

kompira_cloud:
  token: your_kompira_cloud_api_token

general:
  # Zabbixにホストを登録する際のprefix設定
  host_prefix: KompiraCloudNode-

  # Zabbixにホストを登録する際、ホストに自動で割り当てるホストグループ
  # 最低1つ設定する必要があります。
  # 指定されたホストグループがZabbixに存在しない場合、自動で作成します。
  default_groups:
    - Kompira cloud hosts

  # Zabbixにホストを登録する際、ホストに自動で割り当てるテンプレート
  default_templates:
    - Template Module ICMP Ping

  # Kompira cloudでSNMPサービスが動作していることが把握できているホストに
  # 自動で割り当てるテンプレート
  snmp_templates:
    - Template Net Network Generic Device SNMPv2
```

## Usage

Import Kompira cloud node list or snapshot-node list to Zabbix Hosts.

```
# Import Kompira cloud node list to Zabbix Hosts
$ python zabbix_registrar.py https://yourspacename.cloud.kompira.jp/apps/sonar/networks/<networkId>/managed-nodes

# Import Kompira cloud snapshot-node list to Zabbix Hosts
$ python zabbix_registrar.py https://yourspacename.cloud.kompira.jp/apps/sonar/networks/<networkId>/snapshots/<snapshotId>/nodes
```

