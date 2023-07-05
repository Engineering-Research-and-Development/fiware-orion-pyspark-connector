## Docker
#### THIS SECTION IS STILL WORK IN PROGRESS

This connector is available with a docker image containing a working pyspark environment. <br />
The docker image is available downloading it with the command:
```console
docker pull rdenglabpa/fiware-orion-pyspark-connector
```
Then run the docker image with the following command
```console
docker run -it --name CHOOSE_A_CONTAINER_NAME --mount src="PATH_TO_AN_EXISTING_DIRECTORY",dst=/PySpark,type=bind IMAGENAME
```
By running this command, docker creates a container with the chosen name. Then it is possible to mount the connector by simply passing connector files the chosen source directory, findable inside the docker in the /PySpark directory. In this way, it is easy to change connector configuration files and it is possible to easily edit the custom pyspark algorithm from your local machine. <br />
Since the docker container has its own ip address, you need to configure HTTP Server address of the receiver properly. To check the ip address of your docker, run the following command *inside* the container:
```console
hostname -I
```
then change the HTTPServerAddress variable in the configuration file with the output of the command

### If the Context Broker runs on another docker container

To allow communication between docker containers it is necessary to start a bridge and connect. Type in terminal:
```console
docker network create NETNAME
docker network connect NETNAME CONNECTORCONTAINERNAME
docker network connect NETNAME BROKERCONTAINERNAME
```
Once connected the two containers to the network, type in terminal:
```console
docker network inspect NETNAME
```
to see the IP addresses of the two containers. Then, just change the IP address of the HTTPServer in the receiver `conf.py` file and start the algorithm.
