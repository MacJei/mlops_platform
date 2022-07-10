## Базовый Docker-образ
Базовый образ построен на основе официального образа `jupyter/scipy-notebook` и включает в себя следующие дополнительные компоненты:

•	Kerberos

•	Java 8

•	Pyspark kernel для работы cо Spark’ом

•	Pyhive, Impyla

•	ODBC-драйвера для подключения к SQL Server, Oracle, Impala

•	Пакеты из дистрибутива Anaconda для Python 3.7, присутствующие в инсталляторе. Полный список см. здесь https://docs.anaconda.com/anaconda/packages/py3.7_linux-64/ 

•	Python-пакеты для анализа данных, запрошенные пользователями. Список см. в *requirements.txt*

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

Название базового образа  - **base_image**.

При необходимости администратор, либо пользователи с ролью dockerusers могут добавлять в базовый docker-образ новые компоненты. 
