# <img src="https://github.com/MacJei/mlops_platform/blob/main/images/clickhouse(1).svg" width="100"> Clickhouse 
- это колоночная аналитическая СУБД с открытым кодом, позволяющая выполнять аналитические запросы в режиме реального времени на структурированных больших данных, разрабатываемая компанией Яндекс.

Здесь описывается ручная установка. Но если есть опыт с Ansible, то вы можете воспользоваться Ansible плейбуком site-clickhouse.yml.


###### 1. Установка

Кластер Clickhouse нужно развернуть на первой и второй ноде.  
На каждом из Clickhouse-нодов нужно выполнить установку:  

```
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4

echo "deb http://repo.yandex.ru/clickhouse/deb/stable/ main/" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update

sudo apt-get install -y clickhouse-server clickhouse-client
```
Оставьте пароль пользователя по умолчанию пустым.  

###### 3.2. Настройка конфигурации
Конфигурация сервера находится в файле `/etc/clickhouse-server/config.xml`.  
Содержимое файла конфигурации на нодах кластера Clickhouse одинаковое, т.е. его можно и нужно скопировать на все два узла.  
Перед внесением правок в config.xml, сохраните его в оригинальной конфигурации, пригодится, если что-то пойдёт не так.  
В `/etc/clickhouse-server/config.xml` нужно настроить: 1) порт нативного клиента Clickhouse 2) адрес слушателя 3)собственно кластер  

1)Порт нативного клиента Clickhouse 9000 может находиться в конфликте с каким-то другим сервисом кластера. Замените его в строке файла с тэгами:  

`<tcp_port>9090</tcp_port>`

2)По умолчанию сервер слушает на локальном интерфейсе, а не внешнем. Чтобы запускать запросы удаленно, добавьте настройку:  

`<listen_host>0.0.0.0</listen_host>`  

3)Конфигурация кластера находится в между тэгами `<remote_servers><имя_кластера>` и `</имя_кластера></remote_servers>`:  
```
<remote_servers incl="clickhouse_remote_servers" >
       <cluster1>
            <shard>
                <replica>
                    <host>instance-1</host>
                    <port>9090</port>
                </replica>
            </shard>
            <shard>
                <replica>
                    <host>instance-2</host>
                    <port>9090</port>
                </replica>
            </shard>
        </cluster1>
 </remote_servers>
```


###### 3.3. Запуск и останов
`sudo service clickhouse-server start`  
`sudo service clickhouse-server stop`

###### 3.4. Проверка работоспособности
На примерах работы с клиентом Clickhouse:  

Посмотрите базы данных, которые ставятся вместе с clickhouse:
```
clickhouse-client --port 9090 --query="show databases"
```

Если вы выполнили все по инструкции, то в консоли должны увидеть следующий базы:
```
_temporary_and_external_tables
default
system
```

## Clickhouse plugin for Logstash

Если вы уже установили ELK, то установите [logstash-output-clickhouse plugin](https://github.com/mikechris/logstash-output-clickhouse), который позволит вставлять данные в таблицы Clickhouse используя Logshash. Это понадобится в первой лабе.

```
$ cd /usr/share/logstash/
$ sudo bin/logstash-plugin install logstash-output-clickhouse
Validating logstash-output-clickhouse
Installing logstash-output-clickhouse
Installation successful
```

## Работа с клиентом

Обратите внимание на порт, который вы меняли в конфиге сервера.

### Create

```
cat <<END | clickhouse-client --port 9090 --multiline
CREATE TABLE example
  (
     timestamp DateTime,
     referer String
 )
 ENGINE = MergeTree()
 PARTITION BY toYYYYMM(timestamp)
 PRIMARY KEY timestamp
 ORDER BY timestamp
 SETTINGS index_granularity = 8192
END
```

```
clickhouse-client --port 9090 --query="show tables"
```

```
clickhouse-client --port 9090 --query="show create table example"
```

### Insert

`cat train_exploded.json | clickhouse-client --port 9090 --multiline --query="INSERT into gender_age_dist format JSONEachRow"`

### Select

`clickhouse-client --port 9090 --query="select count(uid) from gender_age_dist"`

## Работа с питоновской библиотекой clickhouse-driver

Установите питоновский пакет в среду, где у вас уже установлен Airflow:

`$ pip3 install clickhouse-driver`

Этот пакет использует не REST API, а нативный протокол, так что смотрите внимательно какой порт вы используете для нативного клиента:

```
from clickhouse_driver import Client

client = Client(host='localhost', port=9090)

#
# Select query example
#
query = "select toUnixTimestamp(max(timestamp)) from {}".format(table_name)
res = client.execute(query)
print(res)

#
# insert query example
#  

# export pandas dataframe to json:
values = json.loads(df_flat.to_json(lines=False, orient='records'))
# print(json.dumps(values, indent=4))

query = "INSERT INTO {} VALUES".format(table_name)
res = client.execute(query, values)
```

[Документация](https://clickhouse-driver.readthedocs.io/en/latest/) по пакету очень хороша.

## Работа c REST API

По умолчанию, clickhouse_port должен быть 8123.

### Проверка API

Bash:
`curl  -X GET http://localhost:8123/`

Используйте -v, чтобы получить коды ответа.

Питон:
```python
   uri = 'http://{}:{}'.format(host, clickhouse_port)
   res = requests.get(uri)
   is_success = res.status_code == 200
```

### Запрос

Bash:
`curl  -X GET http://localhost:8123/?query="select+count%28uid%29+from+file_name"`

Питон:
```python
    query = "DESCRIBE {}".format(table)
    uri = requests.get('http://{}:{}/?query={}'.format(host, clickhouse_port, urllib.quote(query)))
    print("clickhouse_check_table: {}".format(query))
    print(uri.text)
    #400 for malformed request, 404 for table does not exists
    return True if uri.status_code == 200 else False
```

### Insert

Bash
`cat data/train_exploded5.json | curl 'http://localhost:8123/?query=INSERT%20INTO%20gender_age_local%20FORMAT%20JSONEachRow' --data-binary @-`

Python:
```python
    query = "INSERT INTO {} FORMAT {}".format(table, data_format)
    query_quote = urllib.parse.quote(query)
    messages = open(message_source).read()
    url = 'http://{}:{}/?query={}'.format(host, clickhouse_port, query_quote)
    resp = requests.post(url, data=messages.encode("utf-8"))
    print(resp.status_code, resp.text)
```

## Ссылки

По этой [ссылке](https://www.altinity.com/blog/2017/12/18/logstash-with-clickhouse) можно прочитать, как подсоединить Logstash напрямую к ClickHouse.

