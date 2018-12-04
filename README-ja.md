# kc2zabbix-sample
Kompira cloudのノード情報をZabbixにインポートするコマンドを提供します。

## 要件
- Zabbix 3.4
- Python 3.6.5


## インストール

### Python のインストール

お使いの環境に沿って、以下のページを参考に Python 3.6 をインストールしてください。

- [Ubuntu](https://www.python.jp/install/ubuntu/index.html)
- [CentOS](https://www.python.jp/install/centos/index.html)
- [Windows](https://www.python.jp/install/windows/install_py3.html)

### Python モジュールのインストール

```
$ pip install zabbix-api requests PyYAML
```

### config.yml の作成

`config.yml.sample` を参考にして、 `config.yml` を作成してください。

```
cp config.yml.sample config.yml
vi config.yml
```

`your_kompira_cloud_api_token` の部分には、お使いのKompira cloudの「全体設定>APIトークン」で発行したトークン文字列を記載してください。

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

## 使用方法

Kompira cloudのノード一覧URL、もしくはスナップショットノード一覧URLを指定することで、Zabbix Hostsとしてデータをインポートします。

```
# ノード一覧をZabbix Hostsに登録
$ python zabbix_registrar.py https://yourspacename.cloud.kompira.jp/apps/sonar/networks/<networkId>/managed-nodes

# スナップショットノード一覧をZabbix Hostsに登録
$ python zabbix_registrar.py https://yourspacename.cloud.kompira.jp/apps/sonar/networks/<networkId>/snapshots/<snapshotId>/nodes
```
