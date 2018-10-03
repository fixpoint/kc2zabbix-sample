# kc2zabbix
Integration Tool for Kompira cloud to zabbix

## Requirements
- Zabbix 3.4
- Python 3.6.5


## Install

### Install python modules
```
pip install zabbix-api requests PyYAML
```

### Make config.yml

Rename config.yml.sample to config.yml

```
zabbix:
  server: http://your.zabbix.name/zabbix
  username: Admin
  password: zabbix

kompira_cloud:
  token: your_kompira_cloud_api_token
```

## Usage

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
