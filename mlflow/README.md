# <img src="https://github.com/MacJei/mlops_platform/blob/main/images/highres_472189526.png" width="250">
Здесь представлена готовая к запуску конфигурация docker-compose для MLFlow с Postgres используемой для хранения метаданных об экспериментах и HDFS хранилищем в котором отдельно хранятся все артефакты и модели.

```
├── README.md
├── docker-compose.yaml  <- конфигурация для запуска контейнеров
├── .env  <- docker-compose.yaml некоторые параметры загружает из данного файла
└── docker_image
    ├── Dockerfile <- файл для создания docker image
    └── start.sh <- конфигурационный файл для работы в контейнере и авто kinit'а для Kerberos
```    
-----------
### Немного об MLflow, его компонентах и архитектуре
> MLflow — это Open Source-Фреймворк, предназначенный для управления жизненным циклом моделей машинного обучения, включая эксперименты, развертывание и реестр моделей.
<img src="https://github.com/MacJei/mlops_platform/blob/main/images/mlflow_infa.png" width="700">

> Основное предназначение данного инструмента — упростить жизнь ML-разработчика, ведь с ростом кол-ва моделей и экспериментов возникает хаос в их хранении, упорядочивании и версионировании: нужно помнить, с какими параметрами обучалась модель, а если было несколько переобучений, то добавляются различные версии моделей. Их как-то нужно сравнивать, чтоб отобрать лучший вариант. Также нужно хранить саму модель и отслеживать основные показатели и метрики. И иметь возможность простым способом воспроизвести эксперименты, в случае если хотите поделиться своими наработками.

> Все эти проблемы решает MLflow. Имея удобный UI-интерфейс, можно просматривать эксперименты, с какими параметрами обучалась модель и какие получились метрики и сравнивать различные версии между собой.
<img src="https://github.com/MacJei/mlops_platform/blob/main/images/mlflow_architectura.png" width="700">

-----------
### Сборка образа для MLflow
0.  получить базовый докер-образ Postgres из публичного реестра:

```sudo docker pull postgres:13.1```

1.	загрузить папку docker_image из данного репозитория
2.	перейти в директорию: 

```cd docker_image```

3.	собрать образ: 

```sudo docker build -t mlflow .```

-----------
### Запуск MLflow
1.	создать директорию mlflow куда скачать из репозитория файлы: **.env, docker-compose.yaml**

```mkdir -p /path/to/mlflow```

2.	перейти в директорию: 

```cd /docker/mlflow/```

3. отредактируйте файлы: **.env и docker-compose.yaml**, замените в них /path/to на ваши пути, login и @REALM на данные вашей системы аутентификации Kerberos

4.	активировать окружение mlflow (в нем установлен docker-compose): 

```sudo conda activate mlflow```

5.	запустить mlflow: 

```sudo docker-compose up -d```

6.	проверить, что приложение запустилось, открыв страницу в браузере: **http://DNS_or_IP:5000**
7.	для остановки приложения выполнить: 

```sudo docker-compose down```

8.	для удаления данных с PostgreSQL выполнить (удалит данные обо всех экспериментах): 

```sudo docker volume rm mlflow_db```

-----------
### Пример использования mlflow на стороне клиента (запускаем в jupyterlab)
```python
import os
os.environ['MLFLOW_TRACKING_URI'] = 'http://DNS_or_IP:5000'
import mlflow
mlflow.set_experiment('test_mlflow')
mlflow.start_run(run_name='first_run')
mlflow.log_param('param_1', 1)
mlflow.log_metric("my_metric", 1)
file = open('config.yaml', 'w')
file.write('alpha: 0.5')
file.close()
mlflow.log_artifact('config.yaml')
mlflow.end_run()
```

-----------
### Замечания насчет работы MLfow на стороне клиента
*В базовый docker образ описанный в репозитории внесены все необходимые изменения для работы с mlflow, замечания ниже написаны для случая, если в какой-то еще среде необходимо логировать в mlflow.
Для работы mlflow на стороне клиента требуется установка mlflow и pyarrow. Пакет pyarrow не указан как зависимость mlflow его требуется установить вручную. Последние версии pyarrow не совместимы с mlflow, экспериментальным путем обнаружено, что он работает с версией `pyarrow==0.16.0`. Запись артефактов в hdfs происходит на стороне клиента, поэтому на клиенте должны быть доступны все необходимые библиотеки hadoop'а и установлены переменные окружения: 
PATH должен указывать на утилиты hadoop’а `/path/to/cloudera/parcels/CDH/bin`, LD_LIBRARY_PATH на `.so` библиотеки hadoop’а.
Для корректной работы из jupyterlab в kernels.json были прописаны следующие переменные окружения:*

"PATH": 
"/path/to/miniconda3/bin:/path/to/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/bin/java/bin:/path/to/cloudera/parcels/CDH/bin"

"LD_LIBRARY_PATH":
"/path/to/cloudera/parcels/CDH/lib64:/path/to/cloudera/parcels/CDH/lib64/debug:/path/to/cloudera/parcels/CDH/lib/hadoop/lib/native:/path/to/cloudera/parcels/CDH/lib/hbase/lib/native:/path/to/cloudera/parcels/CDH/lib/impala/lib:/path/to/cloudera/parcels/CDH/lib/impala/lib/openssl:/path/to/cloudera/parcels/CDH/lib/impala/sbin-debug:/path/to/cloudera/parcels/CDH/lib/impala/sbin-retail:/path/to/cloudera/parcels/CDH/lib/impala-shell/lib/thrift/protocol:"

-----------
### Ссылки
[MLflow: вывод моделей в продакшн и инструмент MLOp](https://habr.com/ru/company/X5Tech/blog/593263/)
  
[Kerberos](https://pro-ldap.ru/tr/zytrax/tech/kerberos.html)
