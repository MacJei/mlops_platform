# MLflow
Здесь представлена готовая к запуску конфигурация docker-compose для MLFlow с Postgres используемой для хранения метаданных об экспериментах и HDFS хранилищем в котором отдельно хранятся все артефакты и модели.

### Сборка образа для MLflow server
0.  получить базовый докер-образ Postgres из публичного реестра:
«sudo docker pull postgres:13.1»
2.	загрузить папку docker_image из данного репозитория
3.	перейти в директорию: 
«cd docker_image»
4.	собрать образ: 
«docker build -t mlflow .»

### Запуск MLflow server
1.	создать директорию mlflow куда скачаете из репозитория файлы: .env, docker-compose.yaml
«mkdir -p /path/to/mlflow»
3.	перейти в директорию: 
«cd /docker/mlflow/»
3.	активировать окружение mlflow (в нем установлен docker-compose): 
«conda activate mlflow»
5.	запустить mlflow server: 
«docker-compose up -d»
7.	проверить, что сервер запустился, открыв страницу в браузере: http://DNS_or_IP:5000
8.	для остановки сервера выполнить: 
«docker-compose down»
10.	для удаления данных PostgreSQL выполнить (удалит данные обо всех экспериментах): 
«docker volume rm mlflow_db»
