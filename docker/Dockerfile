
FROM centos:centos8.4.2105

RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

RUN cd /

RUN yum update -y

RUN yum install -y python3
RUN pip3 install requests


RUN yum install -y java-11-openjdk-devel -y
RUN yum install -y wget
RUN yum install -y unzip

RUN wget https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz
RUN tar xvf spark-3.2.1-bin-hadoop3.2.tgz
RUN mv spark-3.2.1-bin-hadoop3.2/ /opt/spark 
RUN export SPARK_HOME=/opt/spark
RUN export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

RUN pip3 install 'py4j==0.10.9.3'
RUN pip3 install 'pyspark==3.2.1'
RUN pip3 install psutil
RUN pip3 install fiware-pyspark-connector

