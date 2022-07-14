# <img src="https://github.com/MacJei/mlops_platform/blob/main/images/jenkins_logo_icon_167854.png" width="200">
- программная система с открытым исходным кодом на Java, предназначенная для обеспечения процесса непрерывной интеграции программного обеспечения.

Мы используем для двух целей: 

1) контейнеризации приложений (создания продуктовой среды под модель); 

2) актуализация DAG's на продуктовом сервере посредством постонного отслеживания изменений в GitLab.

# I. Установка и запуск
### I.I Через Docker 

Воспользуемся образом докера.

`docker pull jenkinsci/blueocean`

Теперь, внимание! В Dockerfile определен пользователь jenkins с id=1000. Если мы не хотим запускать Jenkins на нашей системе под рутом, нам надо создать пользователя с таким же id. Если у вас в системе нет пользователя с id=1000 (проверьте командой `id 1000`), то создайте пользователя `jenkins`, добавьте его в группу `docker`:

`sudo useradd --uid 1000 --no-create-home -G docker jenkins`

Если же такой юзер имеется, добавьте его в группу docker:

`sudo usermod -G docker your_user_with_id_1000`

Если это ваш текущий юзер, под которым вы эту команду запустили, то перелогиньтесь, чтоб изменения вошли в силу.

Так же заметьте, то мы должны передать и id группы docker на нашем хосте. Посмотрите ее командой: `getent group docker | cut -d: -f3`.

Создайте и запустите контейнер:

```
docker run \
  --name jenkins1 \
  -u 1000:$(getent group docker | cut -d: -f3) \
  --rm \
  -d \
  -p 8070:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkinsci/blueocean
```

Убедитесь, что контейнер `jenkins1` запущен:

`docker ps`

Если что-то пошло не так, запустите без `-d` и смотрите в консоли логи запуска.

Если контейнер запущен, в браузере откройте страницу по адресу `localhost:8070`. Вас просят ввести некий код. Найдите его командой `docker logs jenkins1` которая показывает стандартный вывод контейнера (не торопитесь, запуск занимает некоторое время):

```
INFO: 

*************************************************************
*************************************************************
*************************************************************

Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

686bb244b8f84b2888451cfd67fe9484

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword

*************************************************************
*************************************************************
*************************************************************

```

В Web UI Выберите опцию "Install suggested plugins".

Создайте пользователя-админа (логин и пароль придумайте свой).

Через меню Jenkins->Manage Jenkins->Manage Users->Create User cоздайте пользователя `login_admin` с паролем `password` – он понадобится для запуска сборки через API.

### I.II Локально в Linux
####  Процесс установки:
```
sudo wget -O /etc/yum.repos.d/jenkins.repo \
    https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key
sudo yum upgrade
```
#### Add required dependencies for the jenkins package
```
sudo yum install java-11-openjdk
sudo yum install jenkins
sudo systemctl daemon-reload
```
####  Включить, запустить и узнать статус
```
sudo systemctl enable jenkins.service
sudo systemctl start jenkins.service
sudo systemctl status jenkins.service
```
####  Домашняя директория jenkins:
`/var/lib/jenkins/`

####  Замена пользователя в jenkins:
изменить

`sudo chmod 777 /etc/sysconfig/jenkins`

потом вернуть

`sudo chmod 600 /etc/sysconfig/jenkins`

для ubuntu меняется в файле /etc/sysconfig/jenkins:
```
JENKINS_USER="login"
JENKINS_GROUP="group"

/etc/sysconfig/jenkins
/etc/rc.d/init.d/jenkins
/var/run/jenkins.pid
```
изменить

`sudo chmod 777 /var/run/jenkins.pid`

потом вернуть

`sudo chmod 640 /var/run/jenkins.pid`

далее смена пользователя везде:
```
sudo chown -R login:group /var/lib/jenkins
sudo chown -R login:group /var/cache/jenkins
sudo chown -R login:group /var/log/jenkins
```

И перезапуск jenkins:

`sudo service jenkins restart`

## II. Репозиторий проекта

В имеющемся у вас github репозитории создайте папку и поместите туда следующие файлы со скелетом вашего проекта:

`flask_app.py`:
```python
#
# Simple Flask app
#
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, world!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

`requirements.txt`:
```
Flask==1.0.2
```

`Dockerfile`:
```
FROM ubuntu:18.04
MAINTAINER Ako
RUN apt-get update -y && apt-get install -y python3-pip python-dev build-essential
ADD . /flask-app
WORKDIR /flask-app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["flask_app.py"]
```

## III. Jenkins job

Вернитесь в Jenkins и создайте новую задачу: "Please create new jobs" to get started.

Выберите название проекта `flask` и категорию "Freestyle project".

В секции `Source Code Management`: выберите Git, добавьте ваш репозиторий. 

Добавьте `user/password` в секции Credentials (да, ваш репо должен быть приватным).

* Kind: Username with Password
* Scope: Global
* Username: ваш ник на гитхаб
* Password: ваш пароль на гитхаб
* ID: оставьте пустым
* Description : по желанию

После этого ошибка доступа к репозиторию должна исчезнуть.

В секции `Build Triggers`: выберите "Trigger builds remotely (e.g., from scripts)". Введите название токена `token_nm`.

В секции `Build`: выберите "execute shell", введите:

`cd <dir_name>; docker build -t my-flask-image:latest .; docker run --name my-flask-container --rm -p 5000:5000 -d my-flask-image`  

Сохраните конфигурацию проекта.

## IV. Запуск сборки проекта

В терминале наберите команду:

`curl -X GET http://login_admin:password@localhost:8070/job/flask/build?token=token_nm`

Для отслеживания статуса зайдите на сайт: http://localhost:8070/me/my-views/view/all/

Обратите внимание, что первый запуск будет достаточно длительным, так как docker будет скачивать базовый образ.

Если сборка завершилась успешно, то детали можно посмотреть по ссылке:

http://localhost:8070/me/my-views/view/all/job/flask/lastSuccessfulBuild/

в том числе, лог команды сборки в меню "Console output":

http://localhost:8070/me/my-views/view/all/job/flask/lastSuccessfulBuild/console

Так же точно можно посмотреть и неуспешные сборки.

В случае успешной сборки у вас должен появиться новый образ докера, проверьте командой `docker images`.

## V. Запуск образа проекта

`docker run --rm -p 5000:5000 my-flask-image`

и откройте страничку по адресу `localhost:5000`

Остановите выполнение контейнера по Ctrl+C


## Ссылки
[Пайплайны Jenkins - программирование и настройка. Загружаемые модули](https://infostart.ru/1c/articles/1210995/)

[Jenkins](https://habr.com/ru/post/493580/)
