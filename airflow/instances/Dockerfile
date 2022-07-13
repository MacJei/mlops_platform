# syntax=docker/dockerfile:1
FROM apache/airflow:2.0.2-python3.8

# Copying AirFlow conf files
COPY --chown=airflow:root ./instances/***/cfg/ /path/to/airflow/

# Copying Oracle supporting libs
COPY --chown=airflow:root \
    ./lib/unzip_6.0-23+deb10u2_amd64.deb \
    ./lib/instantclient-basic-linux.x64-21.1.0.0.0.zip \
    ./lib/apache_airflow_providers_oracle-2.0.0-py3-none-any.whl \
    ./lib/cx_Oracle-8.2.1-cp38-cp38-manylinux1_x86_64.whl \
    ./lib/libaio1_0.3.112-3_amd64.deb \
/path/to/airflow/lib/
    
# Copying other libs
# debian libs are from http://ftp.br.debian.org/debian/pool
COPY --chown=airflow:root \
    ./lib/apache_airflow_providers_apache_hive-2.0.1-py3-none-any.whl \
    ./lib/apache_airflow_providers_jdbc-2.0.0-py3-none-any.whl \
    ./lib/cityhash-0.2.3.post9.tar.gz \
    ./lib/pandas-1.3.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl \
    ./lib/libitm1_8.3.0-6_amd64.deb \
    ./lib/binutils-x86-64-linux-gnu_2.31.1-16_amd64.deb \
    ./lib/binutils_2.31.1-16_amd64.deb \
    ./lib/libmpfr6_4.0.2-1_amd64.deb \
    ./lib/libtsan0_8.3.0-6_amd64.deb \
    ./lib/libatomic1_8.3.0-6_amd64.deb \
    ./lib/libasan5_8.3.0-6_amd64.deb \
    ./lib/libstdc++-8-dev_8.3.0-6_amd64.deb \
    ./lib/libbinutils_2.31.1-16_amd64.deb \
    ./lib/libgcc-8-dev_8.3.0-6_amd64.deb \
    ./lib/g++_8.3.0-1_amd64.deb \
    ./lib/manpages-dev_4.16-2_all.deb \
    ./lib/libisl19_0.20-2_amd64.deb \
    ./lib/gcc-8_8.3.0-6_amd64.deb \
    ./lib/libc6-dev_2.28-10_amd64.deb \
    ./lib/manpages_4.16-2_all.deb \
    ./lib/linux-libc-dev_4.19.194-3_amd64.deb \
    ./lib/libmpx2_8.3.0-6_amd64.deb \
    ./lib/libubsan1_8.3.0-6_amd64.deb \
    ./lib/cpp-8_8.3.0-6_amd64.deb \
    ./lib/g++-8_8.3.0-6_amd64.deb \
    ./lib/libmpc3_1.1.0-1_amd64.deb \
    ./lib/binutils-common_2.31.1-16_amd64.deb \
    ./lib/cpp_8.3.0-1_amd64.deb \
    ./lib/libgomp1_8.3.0-6_amd64.deb \
    ./lib/liblsan0_8.3.0-6_amd64.deb \
    ./lib/libc-dev-bin_2.28-10_amd64.deb \
    ./lib/libcc1-0_8.3.0-6_amd64.deb \
    ./lib/gcc_8.3.0-1_amd64.deb \
    ./lib/libquadmath0_8.3.0-6_amd64.deb \
    ./lib/ImpalaJDBC41.jar \
    ./lib/JayDeBeApi-1.2.3-py3-none-any.whl \
    ./lib/pyspark-3.1.2.tar.gz \
    ./lib/py4j-0.10.9.2-py2.py3-none-any.whl \
    ./lib/apache_airflow_providers_apache_spark-2.0.0-py3-none-any.whl \
    # Java libs
    #./lib/openjdk-8-jdk_8u302-b08-1_amd64.deb \
    #./lib/openjdk-8-jre_8u302-b08-1_amd64.deb \
    #./lib/openjdk-8-jre-headless_8u302-b08-1_amd64.deb \
/path/to/airflow/lib/

# Copying Hadoop configs
# spark_conf  is from /path/to/cloudera/parcels/CDH-6.2.1-1.cdh6.2.1.p0.1580995/lib/spark
# hadoop_conf is from /etc/hive/conf.cloudera.hive
#COPY --chown=airflow:root ./hadoop/spark_to_bda_conf/ /etc/
#COPY --chown=airflow:root ./hadoop/spark_to_bda_conf/cloudera/parcels/CDH-6.2.1-1.cdh6.2.1.p0.1580995/ /path/to/cloudera/parcels/CDH-6.2.1-1.cdh6.2.1.p0.1580995

# Installing all avialable libs except ZIP
WORKDIR /path/to/airflow/lib/ 
RUN pip install *.whl --no-index --no-deps 
USER root
RUN sudo dpkg -i *.deb 

USER airflow
RUN pip install ./*.tar.gz --no-index --no-deps 

# The Oracle Client installation
USER root
RUN unzip instantclient-basic-linux.x64-21.1.0.0.0.zip -d /path/to/oracle/ && \ 
	mv /path/to/oracle/instantclient_21_1 /opt/oracle/lib
ENV ORACLE_HOME=/opt/oracle/ \
    LD_LIBRARY_PATH=/path/to/oracle/lib

# Variables section
#ENV SPARK_HOME=/etc/spark_conf \
    #JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/ \
    #HADOOP_CONF_DIR=/etc/hadoop_conf 

#RUN export JAVA_HOME
