# Установка и настройка конфигурации Clickhouse может быть выполнена с использованием Ansible.

# Установка Ansible

Ansible реализована на python, поэтому для ее установки воспользуемся virtualenv.

```
$ cd
$ virtualenv -p /usr/bin/python3 ansenv
$ source ansenv/bin/activate
(ansenv) $ pip install ansible
(ansenv) $ ansible --version
ansible 2.9.4
  config file = None
  configured module search path = ['/home/ubuntu/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/ubuntu/ansenv/lib/python3.6/site-packages/ansible
  executable location = /home/ubuntu/ansenv/bin/ansible
  python version = 3.6.9 (default, Nov  7 2019, 10:44:02) [GCC 8.3.0]
```

# Установка Clickhouse

## Пререквизиты

Склонируйте репо с материалами на ваше устройство и зайдите в директорию:

`cd ansible`

## site-clickhouse.yml

В ansible есть файл site-clickhouse.yml, рассмотрим его содержимое.  

```
#
# Playbook для установки Clickhouse
#
- hosts: clickhouse-nodes
  remote_user: ubuntu
  become: yes
  become_user: root
  roles:
  - { role: clickhouse }
```
## /ansible/roles/clickhouse/tasks/main.yml

Здесь то, что мы бы сами выполняли вручную: добавить репозиторий, его ключ, установить `Clickhouse`, конфиги порта и хоста.

## Файл cluster1 

Найдите файл `roles/clickhouse/files/cluster1` с внутренними доменными именами вашего кластера:

```
instance-1
instance-2
etc
```
Этот файл будет использоваться для создания конфигурации Clickhouse на каждом из узлов кластера.

## Hosts 

Теперь пора дать знать Ansible какие серверы мы назначаем какой группе.

Файл `hosts` в папке ansible (название в нашем случае произвольное, но место по умолчанию - `/etc/ansible/hosts`) содержит разделы группы и имена хостов в этих группах.

Найдите его в этой директории.  
```
[headnode]
instance-1

[node2]
instance-2

[clickhouse-nodes]
instance-1
instance-2
```

## Запуск

Ну вот, у нас готова "нотная тетрадь", или playbook, и запустим процесс конфигурации мы вот такой командой (очевидная аллюзия к игре как по нотам):

```
(ansenv) $ ansible-playbook -i hosts  site-clickhouse.yml

TASK [Gathering Facts] ***********************************************************************
ok: [instance-1]

TASK [java : Install Java 8] *****************************************************************
 [WARNING]: Could not find aptitude. Using apt-get instead

ok: [instance-1]

TASK [clickhouse : Add Clickhouse apt key] *********************************************
ok: [instance-1]
...
```

В конце вы увидите отчет о выполнении задач с разбивкой по хостам:

```
PLAY RECAP ***********************************************************************************************************
instance-2              : ok=15   changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
instance-1              : ok=35   changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

## Повторный запуск ansible-playbook и изменение конфигурации.

Повторный запуск на полностью сконфигурированном сервере должен выдать "все зеленое" - никаких изменений.
А если вы добавили хостов в группы, роли или задачи, то отработать должно только вновь добавленное.
Так же, если в предыдущей конфигурации что-то сломалось, то запуск должен привести конфигурацию снова в декларированный в "нотной тетради" вид.

###### Запуск и остановка
Сервис мы определяем со статусом `started`, например:  

```
# запуск Clickhouse
#
- name: Starting Clickhouse
  service:
   name: clickhouse-server
   state: started
```

Мы могли бы поставить и статус `enabled`, и тогда сервис стартовал бы при загрузке ОС. Но лучше мы оставим вам право запускать сервис по необходимости, чтобы не загружать виртуалки. Его можно запустить на каждой машине с помощью systemctl.  
Clickhouse, на каждой ноде кластера:  
`sudo systemctl start clickhouse`  
`sudo systemctl stop clickhouse`  

Также для запуска можете перезапустить ваш плейбук, и ansible запустит все сервисы за вас, то есть приведет их к желаемому статусу started.
```
source ~/ansenv/bin/activate
cd ansible
ansible-playbook -i hosts site-clickhouse.yml
```
