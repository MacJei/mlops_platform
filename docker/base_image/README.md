## Базовый Docker-образ
Базовый образ построен на основе официального образа `jupyter/scipy-notebook` и включает в себя следующие дополнительные компоненты:

•	Kerberos

•	Java 8

•	Pyspark kernel для работы cо Spark’ом

•	Pyhive, Impyla

•	ODBC-драйвера для подключения к SQL Server, Oracle, Impala

•	Пакеты из дистрибутива Anaconda для Python 3.7, присутствующие в инсталляторе. Полный список см. здесь https://docs.anaconda.com/anaconda/packages/py3.7_linux-64/ 

•	Python-пакеты для анализа данных, запрошенные пользователями. Список см. в *requirements.txt* и *conda_list.txt*

При запуске Docker-контейнера в него автоматически монтируются директории, необходимые для корректной работы с кластером Cloudera:

•	/home/*{username}*/work

•	/shared/jupyterhub

•	/etc/krb5.conf

•	/var/lib/sss/pubconf/krb5.include.d

•	/etc/alternatives/hadoop-conf

•	/etc/alternatives/hive

•	/etc/alternatives/spark-conf

•	/etc/hadoop

•	/etc/hive

•	/etc/spark

•	/path/to/cloudera

При необходимости администратор, либо пользователи с ролью dockerusers могут добавлять в базовый docker-образ новые компоненты. 

## Сборка базового образа
1.	Сохранить на компьютере на котором производится сборка образа файлы из данного репозитория

2.	Перейти в директорию, содержащую файлы для сборки образа и загрузить в директорию java jdk 1.8 (или иную версию), а в директории под odbc_drivers соответствующие драйвера 

3.	Перейти в директорию base_image и выполнить команду 

`cd /path/to/base_image`

`docker build -t base_image .`

в результате будет собран образ с названием **base_image**.

