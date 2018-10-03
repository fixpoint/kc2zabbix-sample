# kc2zabbix_sample
Integration Tool Samples for Kompira cloud to zabbix

## Requirements
- Zabbix 3.4
- Python 3.6.5


## Installation

```
pip install zabbix-api requests PyYAML
```

## Setting

### config.yml の作成

config.yml.sampleを参考にして、config.ymlを作成してください。

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

  # Zabbixにホストを塘路k数る際、ホストに自動で割り当てるテンプレート
  default_templates:
    - Template Module ICMP Ping

  # Kompira cloudでSNMPサービスが動作していることが把握できているホストに
  # 自動で割り当てるテンプレート
  snmp_templates:
    - Template Net Network Generic Device SNMPv2
```

## Usage

### zabbix_registrar


```
python zabbix_registrar.py [kompira cloud target url]
```

Kompira cloudのデータをZabbixに連携する処理を実行します。

引数にはKompira cloudの [管理ノード一覧取得API](https://cloud.kompira.jp/docs/apidoc/#/sonar/get_api_apps_sonar_networks__networkId__managed_nodes__managedNodeId_) または [スナップショットノード一覧取得API](https://cloud.kompira.jp/docs/apidoc/#/sonar/get_api_apps_sonar_networks__networkId__snapshots__snapshotId__nodes) のURLを指定します。


```
python zabbix_registrar.py https://yourspacename.cloud.kompira.jp/apps/sonar/networks/c3805f50-636b-4a75-8c41-e5efcd62ec1d/managed-nodes
2018-09-07 20:12:05,671 - [29277] - INFO - Get node list from KompiraCloud
2018-09-07 20:12:07,315 - [29277] - INFO - Zabbix login: http://your.zabbix.name/zabbix
2018-09-07 20:12:07,451 - [29277] - INFO - Update Host: KompiraCloudNode-192.168.100.1
2018-09-07 20:12:07,847 - [29277] - INFO - Update Host: KompiraCloudNode-192.168.100.2
2018-09-07 20:12:08,160 - [29277] - INFO - Update Host: KompiraCloudNode-192.168.100.3
2018-09-07 20:12:08,448 - [29277] - INFO - Update Host: KompiraCloudNode-192.168.100.4
2018-09-07 20:12:08,753 - [29277] - INFO - Update Host: KompiraCloudNode-192.168.100.5
2018-09-07 20:12:09,068 - [29277] - INFO - Update Host: KompiraCloudNode-192.168.100.6
```
