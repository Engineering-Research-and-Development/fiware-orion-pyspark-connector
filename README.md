# FIWARE Orion PySpark Connector 
The FIWARE Orion PySpark Connector is a FIWARE Generic Enabler (GE) creating a data bridge between the FIWARE Orion Context Broker and PySpark

## What Is Orion PySpark Connector:
Orion PySpark Connector is a FIWARE Generic Enabler (GE) made of a receiver and a replier subcomponents allowing a bidirectional communication between the FIWARE Orion Context Broker (CB) and PySpark. The component works on a low-level socket communication implementing a message passing interface between the two aforementioned counterparts. This interface is equipped with a parser function, hence permitting the creation of both NGSIv2 and NGSI-LD entities ready to use in a custom PySpark algorithm. Once data are preprocessed inside the PySpark evnironment, the component also provide a write-back interface (via REST API) to the Orion CB.


## Why Use Orion PySpark Connector:
Orion PySpark Connector was created with the idea of expanding the FIWARE Orion CB's environment to merge with python's one. Python is currently one of the most used programming languages for data analysis, providing lots of scientific libraries for data processing and visualization. Orion, on the other hand, is a powerful tool allowing the management of context elements and sending updates via subscriptions. This connector is able to open a communication path between these two instruments and to combine the advantages they provide at a little-to-none cost.


## Table of Contents

-   [Component Architecture](#architecture)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage](#usage)
-   [Docker](#docker)
-   [Actual Version Limits](#actual-version-limits)
-   [Roadmap](#roadmap)
-   [License](#license)


## Component Summary
![Pysparkconnector drawio](https://user-images.githubusercontent.com/103200695/171157871-a3904c76-e961-45d5-ad01-507604944ad2.png)


### Receiver Side

The Orion-PySpark receiver is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a PySpark job.
The tool is represented in the following diagram and it is made of:


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

This connector is thought to work as a library component. Information on usage found at: 
[readthedocs.org](docs/usage.md)

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
