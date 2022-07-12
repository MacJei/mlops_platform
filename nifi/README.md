## Apache NiFi <img src="https://github.com/MacJei/mlops_platform/blob/main/images/apache_nifi_logo_icon_167863(1).svg" width="100">
- это open source ETL/ELT-инструмент, который умеет работать со множеством систем

#### Архитектура Apache NiFi 
- включает веб-сервер, контроллер потока и процессор, работающий на виртуальной машине Java (JVM).
<img src="https://github.com/MacJei/mlops_platform/blob/main/images/apache_nifi_architecture.jpg" width="550">

## Apache NiFi Install and Run

NiFi легко использовать как контейнер, давайте так и сделаем.

__Шаг 1.__ Скачиваем образ

`docker pull apache/nifi`

__Шаг 2.__ Запускаем с пробросом на порт хоста 8085:

`docker run --name nifi -p 8085:8080 -d apache/nifi:latest`

__Шаг 3.__ Открываем браузер через прокси на `http://localhost:8085/nifi`

__***__ Либо скачайте docker-compose.yml из данного репозитория, перейдите в директорию где файл, и запустите:

`sudo docker-compose up -d`

Обратите внимание:

* меняем порт на 8085 из-за конфликтов,
* запуск в режиме одного пользователя – берегите от интернета и подсоединяйтесь через прокси,
* запуск может занять некоторое время – не паникуйте,
* все изменения сохраняются внутри контейнера, поетому не удаляете его, а остнанавливайте и перезапускайте командами :`docker stop/start nifi`,
* поскольку NiFi запущен в контейнере, то мы уже не можем использовать localhost в настройках пайплайнов. Везде надо использовать адрес хоста.

### Ссылки:
[Apache NiFi: что это такое и краткий обзор возможностей](https://habr.com/ru/company/rostelecom/blog/432166/)

[Учебное пособие по Apache NiFi Tutorial (Guide, Инструкция)](https://ivan-shamaev.ru/apache-nifi-tutorial-guide/)

[Apache NiFi – Краткое руководство](https://coderlessons.com/tutorials/java-tekhnologii/uznaite-apache-nifi/apache-nifi-kratkoe-rukovodstvo)
