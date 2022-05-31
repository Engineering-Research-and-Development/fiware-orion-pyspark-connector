# FIWARE Orion PySpark Connector


## Table of Contents

-   [What is this connector](#what-is-this-connector)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage](#usage)
-   [Docker](#docker)
-   [Actual Version Limits](#actual-version-limits)
-   [Roadmap](#roadmap)
-   [License](#license)


## What is this connector

### Receiver Side

The Orion-PySpark receiver is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a PySpark job.
The tool is represented in the following diagram and it is made of:


![Pysparkconnector drawio](https://user-images.githubusercontent.com/103200695/171157871-a3904c76-e961-45d5-ad01-507604944ad2.png)



-   **`Connector Library`**: Set of functions and class definition for NGSI Events
-   **`Connector configuration file`**: Configuration file to configure the connector servers and mode.


### Replier Side

The Orion-PySpark replier is currently a library composed by:
- **`Replier Lib`**: Python 3.8 library to import and use in a custom spark job that converts a stream of processed data into a Http request body and sends it with a API request.
- **`Replier configuration file`**: a configuration file to set the API URL, method, some fundamental HTTP headers and the placeholder character for the request body blueprint


## Requirements and installation

The tool source code is written in Python 3.8 and this python version should be installed on the machine running the connector
On linux terminal:

```console
sudo apt update
sudo apt-get install python3.8
sudo apt-get install python3-pip
```

In the `requirements.txt` found in this repository file there is a serie of dependencies useful to load every library used in the connector.
Once downloaded this file, open the terminal in the repository folder and run the following commands:

```console
pip3 install -r requirements.txt
```

Now every required library to run the connector is ready. <br />
**N.B:** The requirements files contains requirement for the connector and the primer. Spark itself is omitted since it is assumed that this library is already installed. If spark is needed, use the following guide:

[Install Spark](https://towardsdatascience.com/installing-pyspark-with-java-8-on-ubuntu-18-04-6a9dea915b5b)



## Usage

### Receiver

Once installed the requirements, it is possible to use the connector by following these steps:
- Load files on the same machine running the spark job
- Modify the `conf.py` file in the repository to set up the IP address and port for both the HTTP Server and the multi-threading socket. 
   - If your PySpark job is running in a docker container, make sure that both the server and multi-thread socket *IP addresses* are the same of that container
   - **Don't use the same (address, port) couple for the HTPP Server and the Sockets**
   -  Currently, the user has to make sure that the chosen ports are free. In future versions, automatic port setting is evaluated for the multi-thread socket.
   -  The "REQUEST_COMPLETENESS" field in this file allow the user to choose if obtain a raw body (JSON Format) or the whole request (with HTTP Headers) to work with a NGSIEvent Object
- Make a subscription to the Orion Broker, inserting the same HTTP server address and port you chose for the configuration file.
- Import all PySpark functions needed for starting the Spark Streaming:
```python
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark import StorageLevel
import connector_lib as connector
```
- Obtain a SparkContext by configuring a SparkSession
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("YOURAPPNAME").getOrCreate()
sc = spark.SparkContext
```
Alternatively, you can create a new SparkContext with your custom configuration
```python
conf = SparkConf().setAppName("YOURAPPNAME").set(YOURRESOURCEMANAGER, YOURMASTERADDRESS[n_nodes])
sc = spark.SparkContext(conf = conf)
```
with *n_nodes > 1*
- Run the connector, passing the SparkContext, the number of seconds of your sliding window and the desired storage level:
```python
record, streamingcontext = connector.Prime(sc, YOUR-DESIRED-NUMBER-OF-SECONDS, storagelevel =StorageLevel.MEMORY_AND_DISK_2)
```
The connector will receive data from the orion broker and its bhaviour is based on both the configuration file (if it accepts only body or whole request) and the type of request arrived on the HTTPServer, automatically deciding if the request contains a NGSIv2 or NGSI-LD data. The function above returns both the stream data to be processed (via PySpark mapping) and the streaming context itself.
- Run the streaming context:
```python
# (YOUR ALGORITHM TO PROCESS record)
ssc.start()
ssc.awaitTermination()
```

### Replier

- Install the requirements for the replier:
```console
pip3 install requests
```
- Modify the `replyconf.py` file to change the Blueprint file path, the API URL and the HTTP method, choosing from "POST", "PUT" and "PATCH". Moreover you need to specify some header fields like the content-type (default application/json) and both fiware service and service_path. Moreover, in this configuration file it is possible to write a custom *placeholder string* to use in the request body blueprint

- In you PySpark job import the receiver library
```python
import replier_lib as replier
```
- **The replier can be used in three different modes: structured, unstructured and semi-structured.**

- *Structured mode*:
   - Create a .txt file with the wanted request body, using the placeholder string decided in the configuration file every time a field has to be completed by the output of the PySpark algorithm
   - If the algorithm produces more than one value, make sure that the incoming values are ordered with respect to the wanted fields
   - Take in account that this method is slower than the others (since files are read from disk) and it fits well when completing large bodies
   - Use the ReplyToBroker function passing the values from the algorithm
```python
response = record.map(lambda x: replier.ReplyToBroker(x))
response.pprint()
```

- *Semi-structured mode*: 
   - Use the SemistructuredReplyToBroker function passing both values and request body with placeholders decided in the configuration file
   - If the algorithm produces more than one value, make sure that the incoming values are ordered with respect to the body fields
   - This method is faster than the structured one, but it fits for small request bodies
   - In case of JSON bodies, remember that properties and string fields must be enclosed in double quotes, so the whole body should be enclosed in single quotes like in the following example (i.e: the replace string configured is %%PLACEHOLDER%%):
```python
response = record.map(lambda x: replier.SemistructuredReplyToBroker(x, '{"example" : %%PLACEHOLDER%% }'))
response.pprint()
```


- *Unstructured mode*: 
   - Use the UnstructuredReplyToBroker function, passing only a complete request body (without placeholder)
   - In case of JSON bodies, remember that properties and string fields must be enclosed in double quotes, so the whole body should be enclosed in single quotes.
   - Have particular care in constructing the request, making sure that no value is escaped
   - Make sure that every value x from the algorithm is casted to string by using the str() keyword
   - This method fits well when the algorithm returns very complex structures (i.e: an entire NGSI Entity) to insert in very small requests
   - This method is the fastest one, but it fits for small request bodies and is more error prone that the others
```python
response = record.map(lambda x: replier.UnstructuredReplyToBroker('{"price" :' + str(x.attrs["price"].value) +' }'))
response.pprint()
```

## Docker
#### THIS SECTION IS STILL WORK IN PROGRESS

This connector is available with a docker image containing a working pyspark environment. <br />
The docker image is available downloading it with the command:
```console
docker pull IMAGE_TO_PUBLISH
```
Then run the docker image with the following command
```console
docker run -it --name CHOOSEACONTAINERNAME --mount src="PathToAnExistingDirectory",dst=/PySpark,type=bind IMAGENAME
```
By running this command, docker creates a container with the chosen name. Then it is possible to mount the connector by simply passing connector files the chosen source directory, findable inside the docker in the /PySpark directory. In this way, it is easy to change connector configuration files and it is possible to easily edit the custom pyspark algorithm from your local machine. <br />
Since the docker container has its own ip address, it is suggested to change the HTTP Server address in the receiver `conf.py` file. To check the ip address of your docker, run the following command *inside* the container:
```console
hostname -I
```
then change the HTTPServerAddress variable in the configuration file with the output of the command

### If the orion broker runs on another docker container

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

## Actual Version Limits

It is important to underline that currently this connector support a single-input single-output connection, limiting to **1** the number of supported spark job per connector. To implement multiple connectors, it is necessary to run another spark job with different addresses.  <br />
It is strongly reccomended to use this connector in local: a future version implementing security will be provided <br />
Currently, receiver supports only subscriptions with **Normalized Format**

### Known Issues

- [x] If the Orion Broker is continuously streaming while the connector is configuring, the multi-thread socket will save the HTTP Server socket as Apache Client, blocking the execution of the whole program. **Fixed on 14/04/22**
- [ ] If some special character is sent from the Orion Broker (i.e Ü or ß) to the receiver, the utf-8 conversion will send it with the escape character *\\* which is not allowed by the JSON Decoder. This will rise an exception. **Working On**


## Roadmap

### Short Term

- [x] Use tests for Receiver. **Completed on 12/04/22**
- [x] Adding a Replier to write back to the broker. **Completed on 13/04/22**
- [x] Adding NGSI-LD support to Receiver **Completed on 13/04/22**
- [x] Use test for Replier **Completed on 14/04/22**
- [x] Find an elegant way to keep Spark socket in memory **Completed on 14/04/22**
- [x] Improve usability for the Receiver **Completed on 15/04/22**
- [x] Adding NGSI-LD support to Replier **Completed on 19/04/22**
- [x] ~~Write a definitive JSON structurer tool~~ **Objective changed on 19/04/22**
- [x] Made a flexible request body constructor **Completed on 19/04/22**
- [ ] Tests for NGSI-LD Support for both receiver and replier side. **Tests ASAP**
- [ ] Test for performances **Tests ASAP**




### Medium Term

- [ ] Make the connector available with a docker image **Working**
- [ ] Subscribing tool
- [ ] Efficiency improvements
- [ ] Better Socket management (automatic ports)
- [ ] Find a **more elegant** way to keep only Spark sockets in memory without blocking the server



### Long Term

- [ ] Evolving this "SISO" connector in a "MIMO" one to support multiple spark jobs
- [ ] Adding security to connections


## License

This software is licensed under [Affero GNU General Public License (GPL) version 3](./LICENSE.txt).


> Please note that software derived as a result of modifying the source code of this software in order to fix a bug or
> incorporate enhancements is considered a derivative work of the product. Software that merely uses or aggregates (i.e.
> links to) an otherwise unmodified version of existing software is not considered a derivative work, and therefore it
> does not need to be released as under the same license, or even released as open source.
