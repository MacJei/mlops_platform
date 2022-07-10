# Use the base datascience image created on the previous step
FROM jupyter/scipy-notebook

USER root

# Install prerequisites
RUN apt-get update && \
 apt-get install -y bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 \
 openssl libkrb5-dev libsasl2-dev gcc make python3-pip unixodbc unixodbc-dev git \
 && rm -rf /var/lib/apt/lists/* 

# Install krb5
RUN apt-get install -y krb5-user

# Install java and pyspark kernels
ADD java /usr/bin/java
RUN rm -rf /opt/conda/share/jupyter/kernels
ADD kernels /opt/conda/share/jupyter/kernels

RUN chmod 777 /usr/bin/java/bin/java && \
 mkdir /home/jovyan/.config/pip

# ADD pip.conf /home/jovyan/.config/pip

#Install anaconda, pyspark
RUN conda install --quiet --yes anaconda pyspark && \
    conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Install pip packages
ADD requirements.txt /home/jovyan
RUN pip install -r /home/jovyan/requirements.txt

# Install ODBC drivers
ADD odbc_drivers /home/jovyan/odbc_drivers

# Install SQL Server ODBC driver
ADD msodbcsql17_17.4.2.1-1_amd64.deb /home/jovyan
RUN ACCEPT_EULA=Y dpkg -i /home/jovyan/odbc_drivers/sqlserver/msodbcsql17_17.4.2.1-1_amd64.deb

# Install Oracle client and ODBC driver
RUN apt-get install -y libaio1 alien
RUN alien -d --script -k /home/jovyan/odbc_drivers/oracle/oracle-instantclient-basic-21.1.0.0.0-1.x86_64.rpm && \
  dpkg -i --force-overwrite oracle-instantclient-basic_21.1.0.0.0-1_amd64.deb && \
  alien -i /home/jovyan/odbc_drivers/oracle/oracle-instantclient-devel-21.1.0.0.0-1.x86_64.rpm && \
  alien -i /home/jovyan/odbc_drivers/oracle/oracle-instantclient-odbc-21.1.0.0.0-1.x86_64.rpm
  
# Install Impala ODBC driver
RUN apt install -y /home/jovyan/odbc_drivers/impala/clouderaimpalaodbc_2.6.5.1005-2_amd64.deb

# Add configs for ODBC drivers
RUN rm -rf /etc/odbcinst.ini && \
 cp /home/jovyan/odbc_drivers/odbcinst.ini /etc && \
 rm -rf /home/jovyan/odbc_drivers

# Install pyhive, impyla
RUN conda install -y pyhive impyla

# Install vowpalwabbit
run apt-get install -y libboost-dev libboost-program-options-dev libboost-system-dev libboost-thread-dev libboost-math-dev libboost-test-dev libboost-python-dev zlib1g-dev cmake && \
  pip install vowpalwabbit

ADD mmlspark_2.11-0.18.1.jar /home/jovyan/jars/mmlspark_2.11-0.18.1.jar
RUN echo "export PATH=\$PATH:/path/to/cloudera/parcels/CDH/bin" >> /etc/profile.d/environment.sh  
RUN echo "export LD_LIBRARY_PATH=/path/to/cloudera/parcels/CDH/lib64:/path/to/cloudera/parcels/CDH/lib64/debug:/path/to/cloudera/parcels/CDH/lib/hadoop/lib/native:/path/to/cloudera/parcels/CDH/lib/hbase/lib/native:/path/to/cloudera/parcels/CDH/lib/impala/lib:/path/to/cloudera/parcels/CDH/lib/impala/lib/openssl:/path/to/cloudera/parcels/CDH/lib/impala/sbin-debug:/path/to/cloudera/parcels/CDH/lib/impala/sbin-retail:/path/to/cloudera/parcels/CDH/lib/impala-shell/lib/thrift/protocol:\$LD_LIBRARY_PATH" >> /etc/profile.d/environment.sh  

# Install git extension to push/pull contents from GitLab repositories
RUN jupyter labextension install @jupyterlab/git
RUN jupyter serverextension enable --py jupyterlab_git
RUN jupyter labextension install jupyterlab-gitlab
RUN jupyter serverextension enable --sys-prefix jupyterlab_gitlab
RUN jupyter labextension install jupyterlab_sparkmonitor # install the jupyterlab extension 
RUN jupyter serverextension enable --py sparkmonitor

RUN rm -rf /home/jovyan/.local \
    mkdir /home/$NB_USER/work && fix-permissions /home/$NB_USER   
    
USER $NB_UID

ENV JAVA_HOME /usr/bin/java
ENV PATH $PATH:/usr/bin/java/bin
ENV SPARK_HOME /path/to/cloudera/parcels/SPARK/lib/spark
ENV HADOOP_MAPRED_HOME=/opt/cloudera/parcels/CDH/lib/hadoop-mapreduce
ENV LD_LIBRARY_PATH=/usr/lib/oracle/21/client64/lib:$LD_LIBRARY_PATH
ENV CLASSPATH=/usr/lib/oracle/21/client64/lib/ojdbc8.jar:$CLASSPATH
ENV ORACLE_HOME=/usr/lib/oracle/21/client64
CMD ["start-notebook.sh"]
