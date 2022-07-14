# Grafana
- свободная программная система визуализации данных, ориентированная на данные систем ИТ-мониторинга.

# Prometheus
- это бесплатное программное приложение, используемое для мониторинга событий и оповещения.


# Установка
Для её установки был скачан репозиторий с гитлаба vegasbrianc/prometheus в /path/to/

Далее в нём используется следующий docker-compose файл:
 
А также в /path/to/grafana/prometheus:
 
И запускается docker-compose
cd /home/sys_cvm_airflow/grafana
docker-compose up -d

WEB UI:

http://DNS_or_IP:3000/dashboards

http://DNS_or_IP:9090

http://DNS_or_IP:9100


