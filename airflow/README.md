# <img src="https://github.com/MacJei/mlops_platform/blob/main/images/wordmark_1.png" width="400">
- это инструмент для создания, мониторинга и оркестрации batch-процессов обработки данных.

### Сущности Airflow:
•	DAG

•	Задача

•	Оператор

•	DAG run

•	Execution_date

•	Variables

•	Connections

•	Hooks

-----------
#### Airflow DAG
- это направленный ацикличный граф. Другими словами, он представляет из себя пайплайн - некоторое смысловое объединение ваших задач, которые вы хотите выполнить в строго определенной последовательности по определенному расписанию.

При этом вы можете явно видеть каждый узел (задачу) и его связь с другими узлами.
<img src="https://github.com/MacJei/mlops_platform/blob/main/images/dag.PNG" width="600">

#### Airflow Task
Каждая задача (т.н. Task'a) - это какая-то операция с данными.

Например:

•	загрузка данных из различных источников

•	агрегирование данных

•	индексирование

•	очистка от дубликатов

•	сохранение полученных результатов и прочие ETL-процессы.

На уровне кода, задачи могут представлять собой Python-функции или Bash-скрипты.

Задачи могут выполняться как последовательно, так и параллельно.

Разработчик, проектируя DAG, закладывает набор операторов, на которых будут построены задачи внутри DAG’а

#### Airflow Operator
— это кусочки кода, ответственные за выполнение какого-либо конкретного действия (задачи).

И если задачи описывают, какие действия выполнять с данными, то операторы — как эти действия выполнять.

В AirFlow богатый выбор готовых к использованию операторов.

Ознакомиться с полным перечнем доступных операторов - [см. в официальной документации](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/index.html)

#### DAG Run
Запуск DAG (т.н. DAG Run) - это инициализированный даг, которому присвоена своя дата исполнения (т.н. execution_date).

DAG Run одного DAG могут работать параллельно если задачи сделаны идемпотентными.
**Идемпотентность** -   это свойство объекта при повторном применении операции к объекту всегда возвращать один и тот же результат.
В контексте Airflow это значит, что если сегодня вторник, а мы перезапускаем задачу за прошедший понедельник, то задача запустится так, как будто для нее сейчас прошлый понедельник. Другими словами, запуск или перезапуск задачи за какую-то дату в прошлом никак не должен зависеть от того, когда эта задача фактически запускается. И чтобы идемпотентность работала - используется переменная execution_date.

#### Execution_date
Airflow разрабатывался как инструмент для решения задач, связанных с обработкой данных. В пакетном (batch) режиме мы обычно обрабатываем крупную порцию данных только тогда, когда она готова.

Поэтому когда мы запускаем ежедневный пайплайн, то с большой вероятностью захотим обрабатывать данные за вчера.

<img src="https://github.com/MacJei/mlops_platform/blob/main/images/execution_date.PNG" width="600">

Именно поэтому execution_date будет равен левой границе интервала, за которой мы обрабатываем данные.

Например, чтобы сегодня в 19:54 по UTC стартовал даг, мы должны в execution_date указать вчерашнюю дату с тем же временем.

Если мы запускаем пайплайн каждый час, то чтобы он отработал в 12 часов дня нужно в execution_date указать 11 часов утра.

#### Variables 
- это переменные. в них хранятся вещи, которые нужны для запуска пайплайнов. Например, там лежат названия популярных схем в Hive, пути к часто используемым директориям в HDFS, идентификатор окружения и прочее.  

`from airflow.models import Variable` 

#### Hooks
- это интерфейсы для внешних источников и баз данных, часто выступающие ключевым звеном для работы операторов и сенсоров.

`from airflow.hooks.base_hook import BaseHook`

#### Сonnections
это сущность, в которой хранится информация о подключении к внешним источникам. В Airflow поддерживается множество источников: от банальных http и ftp, заканчивая популярными базами данных и облачными провайдерами.

-----------
## Установка и запуск Airflow
Airflow состоит из трех компонент:

•	Scheduler

•	Web UI

•	Worker

#### Список предустановленного ПО
•	Linux OS

•	Docker Community Edition (CE)

•	Docker Compose (v1.27.0 или новее)

Для установки данных компонентов Docker можно использовать [инструкцию](https://github.com/MacJei/mlops_platform/tree/main/docker)

#### Установка ПО
__1.__ Скачиваем необходимые образы
```bash
sudo docker pull apache/airflow:2.0.2-python3.8
sudo docker pull redis:latest
sudo docker pull postgres:13
```
__2.__ Настройка системы каталогов

a. Создать каталог и подкаталоги Airflow:
```bash
sudo mkdir -p /path/to/airflow/{instances,lib,log}
sudo cd /path/to/airflow
```
b. Создать каталог и подкаталоги Инстанса:
```bash
sudo mkdir -p instances/имя_инстанса/{cfg,dags,plugins}
```
c. Произвести настройки доступов на каталоги и файлы:
```bash
sudo chown root:airflow .
sudo chown root:airflow *
sudo chown airflow:airflow log
sudo chmod 754 *
sudo chmod 755 . instances lib log
sudo chown root:airflow lib/*
```
d. Настроить файловые доступы для каждого инстанса, выполнив команду:
```bash
sudo sh set_inst имя_инстанса
```

__3.__ Настройка SSL

a. Создаем директорию и ограничиваем доступ к ней и переносим туда файлы с расширением .cer и .key
```bash
mkdir "/etc/airflow_ssl/"
chmod 700 "/etc/airflow_ssl/"
chown root:airflow "/etc/airflow_ssl/"
setfacl -m other:--x "/etc/airflow_ssl/"
setfacl -m group::--x "/etc/airflow_ssl/"
```
b. Права на файлы в директории должны быть следующего вида --rw-r--r–, если не так, то надо исправить
```bash
chmod 644 -R /etc/airflow_ssl/*
```
c. Добавляем ссылки на ssl ключи в файл **airflow.cfg**
```bash
# Paths to the SSL certificate and key for the web server. When both are
# provided SSL will be enabled. This does not change the web server port.
web_server_ssl_cert = /etc/airflow_ssl/cert_name.cer
 
# Paths to the SSL certificate and key for the web server. When both are
# provided SSL will be enabled. This does not change the web server port.
web_server_ssl_key = /etc/airflow_ssl/key_name.key
```
d. Добавляем строку по импорту директории в файл **docker-compose.yaml** airflow-webserver:
```yaml
…
volumes:
  - /etc/airflow_ssl:/etc/airflow_ssl
…
```

__3.__ Настройка файлов

a. Файл **airflow.cfg**

Правим пути на свои путем замены - /path/to, указываем путь к ssl сертификатам, можно настроить Kerberos аутентификацию и многое другое.

b. Файл **webserver_config.py**

Система настроена на аутентификацию LDAP. Необходимо настроить словарь AUTH_ROLES_MAPPING в файле /path/to/airflow/instances/имя_инстанса/cfg/webserver_config.py, прописав соответствие ролей Airflow и доменных групп. Ниже показан пример для инстанса:
```bash
AUTH_ROLES_MAPPING = {
  "CN=GROUP_NAME,OU=Группы доступа,DC=...,DC=ru": ["User"],  
  "CN=GROUP_NAME,OU=Группы доступа,DC=...,DC=ru": ["Op"],
  "CN=GROUP_NAME,OU=Группы доступа,DC=...,DC=ru": ["Admin"],
}
```
Первые две строки - это роли по умолчанию, для последней строки группа была создана отдельно.

c. Файл **docker-compose.yaml**

Файл задает общие для всех инстансов настройки и сборки докер-сервисов, а также маппинг внешних дисковых ресурсов в контейнеры инстансов. При создании нового инстанса этот файл, как правило, не требует модификации, т.к. все частные параметры, относящиеся к конкретному инстансу, вынесены в файлы dockerfile и .env.

d. Файл **Dockerfile**

Файл /path/to/airflow/instances/имя_инстанса/Dockerfile описывает процесс сборки докер-образа инстанса. В нем перечислены команды, выполняемые на этапе сборки, а также задается имя базового докер-образа Airflow, на основе которого производится сборка всех инстансов.

Общая последовательность шагов:

1. Следует задать имя базового образа через FROM. 

2. Актуализировать путь к каталогу cfg данного инстанса в операторе копирования конфигов с сервера в собираемой докер-образ (оператор COPY).

3. Актуализировать список устанавливаемых библиотек. Отдельно сначала делается операция копирования списка библиотек в образ инстанса (этот список необходимо актуализировать), а затем, идет несколько циклов, пробегающих по директории со скопированными библиотеками и производящих установку каждой. Таких циклов несколько, по одному для каждого вида библиотек: whl, deb, tar.gz. Все библиотеки должны быть заранее загружены в каталог /path/to/airflow/lib.

4. Проверить корректность других операторов (user, ENV и др.). При этом следует иметь в виду, что секция установки из исходных кодов (файлов tar.gz) должна работать под пользователем airflow, а deb - под root. 

f. Файл **.env**

Файл /path/to/airflow/instances/имя_инстанса/.env, является расширением файла docker-compose.yaml для инстанса, он содержит блок обязательных параметров и блок необязательных.

К обязательным параметрам, уникальные значения которых требуется задавать для каждого инстанса, относятся:

Имя инстанса - DOCKER_INSTANCE_NAME

Номера портов, на которых будут работать сервисы контейнеров - параметры вида DOCKER_PORTS_XXXX.

Выбирать значения портов следует на основе следующих требований:

Две последние цифры портов во всех переменных DOCKER_PORTS_XXXX должны совпадать

Порты не заняты на сервере установки. Проверить это можно при помощи команды netstat -tulpn | grep LISTEN | sort -nk4.

К необязательным параметрам, в частности относится AIRFLOW__CORE__LOAD_EXAMPLES, с помощью которого можно отключить даги-примеры от Apache.

Пример заполнения .env для инстанса:
```bash
# Mandatory parameter set
DOCKER_INSTANCE_NAME=instance_name
AIRFLOW_IMAGE_NAME=apache/airflow:2.0.2-${DOCKER_INSTANCE_NAME}
DOCKER_PORTS_FLOWER=5593
DOCKER_PORTS_WEBSERVER=8093
DOCKER_PORTS_REDIS=6393
 
# Optional parameter set. Comment out ones to go to the default values defined in docker-compose.yaml
# Changing the corresponding values in the airflow.cfg file is not required
AIRFLOW__CORE__LOAD_EXAMPLES='false'
#AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION = 'false'
```
Параметр AIRFLOW_IMAGE_NAME задает имя будущего докер-образа инстанса. В тег докер-образа следует включить номер версии Airflow из базового образа (2.0.2 в данном примере).

__4.__ Работа с инстансом

a. Сборка инстанса:
```bash
sudo sh init имя_инстанса
```
В ходе сборки docker-compose сканирует все файлы внутри каталога, откуда производится запуск (/path/to/airflow). Поэтому необходимо использовать sudo, чтобы, в том числе, получить доступ к файлам dags и cfg всех инстансов.

В результате появится следующий вывод, который говорит об успешном завершении сборки докер-образа инстанса:
```bash
airflow-init_1 | airflow already exist in the db
airflow-init_1 | 2.0.2
instance_name_airflow_airflow-init_1 exited with code 0
```
проверить появление образа в docker:
```bash
docker images
```

b. Запуск инстанса:
```bash
sh up имя_инстанса
```
Проверку запуска можно осуществить посредством команды `docker ps` - она выведет список контейнеров всех запущенных инстансов. Имена контейнеров будут начинаться с названий инстансов.

Далее следует убедиться, что Airflow доступен через веб-браузер. Для этого нужно открыть ссылку вида https://host:port, где

host – хост сервера, на котором проводилась установка;
port – значение из параметра DOCKER_PORTS_WEBSERVER из файла instances/имя_инстанса/.env.

После этого осуществить вход в Airflow, используя доменную УЗ.

c. Останов инстанса:
```bash
sh down имя_инстанса
```
В результате данной команды будут остановлены и удалены докер-контейнеры данного инстанса. Все настройки и данные Airflow при этом сохранятся, т.к. они располагаются в docker volumes в соответствующих каталогах на сервере.

d. Рестарт инстанса:
```bash
sh restart имя_инстанса
```
