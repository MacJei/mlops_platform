# <img src="https://github.com/MacJei/mlops_platform/blob/main/images/docker_official_logo_icon_169250.png" width="250">
Среда для развертывания и управления приложениями в виде пакетов, называемых контейнерами.  


<img src="https://github.com/MacJei/mlops_platform/blob/main/images/Docker-API-infographic-container-devops-nordic-apis.png" width="700">


*Инструкция по развертыванию написана для Oracle Linux 7. Предполагается, что установка проводится на компьютере с доступом в интернет. Установка и настройка производится под пользователем root либо через sudo.*

### Описание установки и настройки ПО:
1. Установить пререквизиты (устранение зависимостей): 

```
a.  sudo yum-config-manager –enable ol7_addons
b.  sudo yum install -y yum-utils device-mapper-persistent-data lvm2 container-selinux
```


2. Установить Docker Engine – Community: 

```sudo yum install docker-ce docker-ce-cli containerd.io```

3. Проверить все ли корректно установилось:

```docker --version```

4. Запустить Docker: 
```
a.	sudo systemctl start docker
b.	sudo systemctl start docker.service
```

5.	Создать группу docker и добавить пользователей в группу для запуска без sudo:
```
a.	sudo groupadd docker
b.	sudo usermod -aG docker <имя_пользователя>
c.	sudo systemctl restart <имя_пользователя> or newgrp docker
d.	docker image ls
```

6. Проверить работу ПО:

```sudo docker run hello-world```

7. Установка docker-compose:
```
a.	sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
b.	sudo chmod +x /usr/local/bin/docker-compose
c.	sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
d.	docker-compose --version 
```

8. Установка docker-machine:
```
a.	sudo base=https://github.com/docker/machine/releases/download/v0.16.0 \
  && curl -L $base/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine \
  && sudo mv /tmp/docker-machine /usr/local/bin/docker-machine \
  && chmod +x /usr/local/bin/docker-machine
b.  docker-machine version
```

9. Установка docker-registry и настройка приватного Docker-репозитория:

`docker pull registry`

[Настраиваем приватный Docker-репозиторий](https://habr.com/ru/post/320884/)

[Настройка частного реестра Docker](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-18-04-ru)

Чтобы к нему подключиться нужно на серверах с docker добавить информацию о docker-registry:
```
a.  cd /etc/docker
b.  sudo touch daemon.json
c.  sudo chmod 777 /etc/docker/daemon.json
```

и добавить в этот файл следующий код и перезапустить docker:
```
a. {
    "insecure-registries" : [ "DNS_or_IP:5000" ]
  }
b.  sudo systemctl restart docker
```

Ссылки для docker-registry:

https://*DNS_or_IP*:5000/v2/node-exporter/tags/list

https://*DNS_or_IP*:5000/v2/_catalog

Пример использования docker-registry:
```
docker tag base_image DNS_or_IP:5000/base_image
docker push DNS_or_IP:5000/base_image
docker pull DNS_or_IP:5000/base_image
```

На сервере создаем группу docker, которой выдаем права на выполнение следующих команд docker: 
```diff, events, history, images, info, inspect, logs, port, ps, search, stats, top, version, build, commit, export, import, load, login, logout, pull, push, save, rmi, tag, run(*), start(*), stop(*), rm(*)```

`(*)`  - на команды, отмеченные `(*)` для безопасности права давать только через скрипты-обертки.
