#!/bin/bash

echo "installing python 3.8"
sudo apt update -y
sudo apt-get install python3.8 -y
sudo apt-get install python3-pip -y
echo "installed python 3.8"

echo "installing Java 11"
sudo apt-get install -y java-11-openjdk-devel -y
sudo apt-get install -y wget
sudo apt-get install -y unzip
echo "installed Java 11"

echo "installing Spark 3.2.1"
wget https://dlcdn.apache.org/spark/spark-3.2.1/spark-3.2.1-bin-hadoop3.2.tgz
tar xvf spark-3.2.1-bin-hadoop3.2.tgz
mv spark-3.2.1-bin-hadoop3.2/ /opt/spark 
export SPARK_HOME=/opt/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
echo "installed Spark 3.2.1"

echo "installing python requirements: requests"
pip3 install requests
echo "installing python requirements: py4j"
pip3 install 'py4j==0.10.9.3'
echo "installing python requirements: pyspark"
pip3 install 'pyspark==3.2.1'
echo "installed every python dependency"
echo "installing the connector"
echo "downloading repository"
wget https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/archive/refs/heads/main.zip
unzip main.zip
echo "repository downloaded and unzipped"
mkdir ../PySpark/
mv fiware-orion-pyspark-connector-main/receiver/connector_lib.py ../PySpark/
mv fiware-orion-pyspark-connector-main/receiver/connectorconf.py ../PySpark/
mv fiware-orion-pyspark-connector-main/replier/replier_lib.py ../PySpark/
mv fiware-orion-pyspark-connector-main/replier/replyconf.py ../PySpark/
rm -r fiware-orion-pyspark-connector-main
rm main.zip
echo "connector succesfully imported"
