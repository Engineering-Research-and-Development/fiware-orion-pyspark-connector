## Docker
#### THIS SECTION IS STILL WORK IN PROGRESS

This connector is available with a docker image containing a working pyspark environment. The environment consists of a spark node with a set of data analysis libraries.<br />


The docker image is available downloading it with the command:
```console
docker pull quay.io/darthfinal3/fiware-pyspark-connector
```
Then run the docker image with the following command
```console
docker run -it --name pyspark_master --mount src="PATH_TO_AN_EXISTING_DIRECTORY",dst=/PySpark,type=bind quay.io/darthfinal3/fiware-pyspark-connector
```
By running this command, docker creates a container with the chosen name. Then it is possible to mount the connector by simply passing algorithm files in the chosen source directory, findable inside the docker in the /PySpark directory. In this way, it is easy to change connector configuration or processing steps by simply chaning the custom pyspark algorithm from the local machine. <br />
Since the docker container has its own ip address, you need to configure HTTP Server address of the receiver properly. To check the ip address of your docker, run the following command *inside* the container:
```console
docker exec -it pyspark_master bash
hostname -I
```
and use the IP address to set the HTTPServer endpoint configuration

This image contains a minimal set of popular data analysis libraries, such as:
- numpy
- pandas
- matplotlib
- seaborn
- scipy
- simpy
- scikit-learn
And also contains the connector's library itself, with its dependencies:
- fiware-pyspark-connector
  - py4j
  - pyspark
  - requests
  - psutil
 

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
      - master.env
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
    env_file:
      - worker.env
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

This docker compose configures two kind of nodes and a network. Two environment files are provided, one for the master node, the other for worker nodes. In particular, master node configuration is useful to set up the spark cluster master node IP and workload, while the worker nodes can be configured to allocate a precise amount of resources, as it follows:

- **SPARK_MASTER:** Spark master url
- **SPARK_WORKER_CORES:** Number of cpu cores allocated for the worker
- **SPARK_WORKER_MEMORY:** Amount of ram allocated for the worker (format: 512M, 1G, etc.)
- **SPARK_DRIVER_MEMORY:** Amount of ram allocated for the driver programs (format: 512M, 1G, etc.)
- **SPARK_EXECUTOR_MEMORY:** Amount of ram allocated for the executor programs (format: 512M, 1G, etc.)
- **SPARK_WORKLOAD:** The spark workload to run (can be any of master, worker, submit; for workers use **worker**) 
- **SPARK_LOCAL_IP:** local ip for worker, usually the container name

It is possible to set up any amount of workers, even with different configurations. To do that, copy the "worker template" from the above docker compose and customize it following the criteria explained in the above list.

Said so, the installation folder should have the following structure:

- **INSTALLATION_FOLDER**
- ------ worker.env
- ------ master.env
- ------ jobs

Where the two env files are the ones needed to inject `env` variables in docker compose, while the **jobs** folder is the one used to load the algorithms you want to run with the pyspark connector. **WARNING: the jobs folder is mandatory, otherwise the docker compose will create a not modifiable folder**

By using docker compose it is possible to expand the number of libraries to install by adding commands in docker compose:

```yaml
version: "3.3"
services:
  spark-master:
    image: quay.io/REPOACCOUNT/fiware-pyspark-connector
    container_name: pyspark_master
    command: bash -c "pip3 install library"
    ports:
      - "9090:8080"
      - "7077:7077"
    volumes:
       - ./apps:/opt/spark-apps
       - ./data:/opt/spark-data
       - ./jobs:/opt/spark/data
    env_file:
      - master.env
    networks:
      pyspark_net:
        ipv4_address: 172.28.1.1
    logging:
      options:
          max-size : "200m"
```
