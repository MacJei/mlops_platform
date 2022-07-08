FROM ubuntu:focal-20220113

# Создаем директорию
RUN mkdir -p /mlflow/mlruns

WORKDIR /mlflow

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN echo "export LC_ALL=$LC_ALL" >> /etc/profile.d/locale.sh
RUN echo "export LANG=$LANG" >> /etc/profile.d/locale.sh

# Обновляем и устанавливаем нужные пакеты
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    libpq-dev \
    krb5-user \
    cron

# Устанавливаем python библиотеки
RUN pip3 install psycopg2 pyarrow==0.16.0 mlflow==1.23.1 protobuf==3.20.0

COPY ./start.sh ./start.sh
RUN chmod +x ./start.sh

# Чистим за собой кэши
RUN rm -rf /usr/local/bundle/cache/*.gem
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Запускаем скрипт, при старте контейнера, который запустит все остальное.
CMD ["./start.sh"]
