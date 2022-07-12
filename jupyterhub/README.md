## Conda <img src="https://github.com/MacJei/mlops_platform/blob/main/images/file_type_conda_icon_130674.svg" width="64">
Менеджер пакетов и система управления виртуальными окружениями.

## JupyterHub <img src="https://github.com/MacJei/mlops_platform/blob/main/images/jupyter_logo_icon_169452.svg" width="64">
Многопользовательский сервер, управляющий однопользовательскими Jupyter Notebook. 

-----------
#### Создать виртуальное окружения Conda:

•	Название окружения – jupyterhubenv

•	Путь к окружению - /opt/miniconda3/envs/jupyterhubenv

•	Файл конфигурации - /opt/miniconda3/envs/jupyterhubenv/jupyterhub_config.py

Запускается по адресу https://DNS_or_IP:8000

-----------
#### Установка Conda
__1.__	Загрузить инсталлятор https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

__2.__	Сравнить хэши, выполнив команду 

`sha256sum path/to/file`

__3.__	Выполнить команду 

`bash Miniconda3-latest-Linux-x86_64.sh`

__4.__	Следовать инструкциям инсталлятора 

a.	Принять лицензионное соглашение

b.	Указать директорию для установки /opt/miniconda3

c.	На вопрос “Do you wish the installer to initialize Anaconda3 by running conda init?” ответить “yes”

__5.__	Закрыть и открыть терминал, либо ввести команду 

`source ~/.bashrc`

-----------
#### Установка JupyterHub

__1.__	Создать окружение conda 

`conda create -n jupyterhubenv python=3.7`

__2.__	Активировать окружение 

`conda activate jupyterhubenv`

__3.__	Установить JupyterHub 

`conda install -c conda-forge jupyterhub`

__4.__ Установить необходимые вам библиотеки

`pip install -r /path/to/requirements.txt`

__5.__ Протестируйте вашу установку. Если они установлены, эти команды должны возвращать содержимое справки пакетов:
```
jupyterhub -h
configurable-http-proxy -h
```

__6.__ Создаем директорию для SSL сертификатов для работы jupyterhub
```bash
mkdir -p /etc/jupyterhub/ssl/
chmod 700 "/etc/jupyterhub/ssl/"
```

Меняем права на ключи (для всех):
```bash
sudo chmod 600 name.cer
sudo chmod 600 name.key
```

__7.__ Создаем общую директорию для обмена файлами среди пользователей
```bash
sudo mkdir -p "/shared/jupyterhub"
sudo chmod 774 "/shared/jupyterhub/"
sudo chown :jupyterhub -R "/shared/jupyterhub/"
```

-----------
#### Настройка компонент
__1.__	Активировать виртуальное окружение conda

`conda activate jupyterhubenv`

__2.__	Установить DockerSpawner (требуется для работы JupyterHub с docker-контейнерами) 

`pip install dockerspawner`

__3.__	Заменить файл */opt/miniconda3/envs/jupyterhubenv/lib/python3.7/site-packages/dockerspawner/dockerspawner.py* файлом **dockerspawner.py** из репозитория

__4.__	Положить в директорию */opt/miniconda3/envs/jupyterhubenv* файл **jupyterhub_config.py** также из репозитория

#### Запуск и остановка JupyterHub
##### Запуск
__1.__	Перейти в директорию /opt/miniconda3/envs/jupyterhubenv, отредактировать файл **jupyterhub_config.py**, добавив в конфиг *c.Authenticator.admin_users* имя пользователя

`cd /opt/miniconda3/envs/jupyterhubenv/`

__2.__ Активировать окружение 

`conda activate jupyterhubenv`

__3.__ Запустить jupyterhub командой 

`nohup jupyterhub > jupyterhub.log &`

__4.__ Если не перезапустилась, то значит зависла сессия каких-то процессов, и надо их отключить вручную.
```bash
ps -aux | grep jupyter
kill $(ps -ef | grep "jupyter" | awk '{print $2}')
kill -9 key
```

##### Остановка
__1.__	Залогиниться в web-интерфейс JupyterHub ( https://DNS_or_IP:8000 ) под пользователем-администратором

__2.__	Нажмите Control Panel -> Admin -> Shutdown Hub


## Взаимодействие компонент
-----------
#### Когда пользователь вводит логин/пароль в JupyterHub, то 

__1.__	происходит его авторизация на сервере https://DNS_or_IP

__2.__	далее автоматически выполняется авторизация в керберос с помощью команды kinit и переданного пользователем пароля. Требует наличия на сервере учетки с доменной авторизацией.

__3.__	Запускается Docker-контейнер с установленным внутри него Jupyter Notebook. При запуске контейнера пользователь может выбрать на основе какого образа запускать контейнер. Если контейнер запущен из базового образа, то внутри него можно выбирать ядро выполнения Jupyter – стандартное, либо pyspark с заданным лимитом driver memory.
