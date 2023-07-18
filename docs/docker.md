## Docker
#### THIS SECTION IS STILL WORK IN PROGRESS

This connector is available with a docker image containing a working pyspark environment. <br />
The docker image is available downloading it with the command:
```console
docker pull quay.io/darthfinal3/fiware-pyspark-connector
```
Then run the docker image with the following command
```console
docker run -it --name CHOOSE_A_CONTAINER_NAME --mount src="PATH_TO_AN_EXISTING_DIRECTORY",dst=/PySpark,type=bind IMAGENAME
```
By running this command, docker creates a container with the chosen name. Then it is possible to mount the connector by simply passing algorithm files in the chosen source directory, findable inside the docker in the /PySpark directory. In this way, it is easy to change connector configuration or processing steps by simply chaning the custom pyspark algorithm from the local machine. <br />
Since the docker container has its own ip address, you need to configure HTTP Server address of the receiver properly. To check the ip address of your docker, run the following command *inside* the container:
```console
docker exec -it pyspark_master bash
hostname -I
```
and use the IP address to set the HTTPServer endpoint configuration

### Running Through Docker-Compose

The preferred way to run the connector is trhough docker-compose. In this way it is possible to setup a pyspark cluster with driver nodes:

```yaml

version: "3.3"
services:
  spark-master:
    image: quay.io/REPOACCOUNT/fiware-pyspark-connector
    container_name: pyspark_master
    ports:
      - "9090:8080"
      - "7077:7077"
    volumes:
       - ./apps:/opt/spark-apps
       - ./data:/opt/spark-data
       - ./jobs:/opt/spark/data
    environment:
      - SPARK_LOCAL_IP=spark-master
      - SPARK_WORKLOAD=master
    networks:
      pyspark_net:
        ipv4_address: 172.28.1.1
    logging:
      options:
          max-size : "200m"
      
      
  spark-worker-x:
    image: quay.io/REPOACCOUNT/fiware-pyspark-connector
    container_name: pyspark_worker_a
    ports:
      - "9091:8080"
      - "7000:7000"
    depends_on:
      - spark-master
    environment:
      - SPARK_MASTER=spark://spark-master:7077
      - SPARK_WORKER_CORES=1
      - SPARK_WORKER_MEMORY=1G
      - SPARK_DRIVER_MEMORY=1G
      - SPARK_EXECUTOR_MEMORY=1G
      - SPARK_WORKLOAD=worker
      - SPARK_LOCAL_IP=spark-worker-x
    volumes:
       - ./apps:/opt/spark-apps:rw
       - ./data:/opt/spark-data:rw
    networks:
      pyspark_net:
        ipv4_address: 172.28.1.2
    logging:
      options:
          max-size : "200m"

          
networks:
  pyspark_net:
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
```    

This docker compose configures two kind of nodes and a network. Each configuration is self-explainable. The only thing to remark is the additional folder mapping provided (./jobs:/opt/spark/data). Before launching the docker-compose, it is necessary to create a *jobs* folder in which to put the algorithms, otherwise the folder is created in restricted access mode and cannot be modified runtime. It is possible to add as much pyspark workers as needed and allocate the desired amount of resources for each of them.
