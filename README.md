# FIWARE Orion PySpark Connector 
The FIWARE Orion PySpark Connector is a FIWARE Generic Enabler (GE) creating a data bridge between the FIWARE Orion Context Broker and PySpark



## Table of Contents

-   [What Is Orion PySpark Connector](#what-is)
-   [Why Use Orion PySpark Connector](#why-use)
-   [Component Architecture](#component-architecture)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage](#usage)
-   [Docker](#docker)
-   [Roadmap](#roadmap)
-   [License](#license)



## What Is Orion PySpark Connector
Orion PySpark Connector is a FIWARE Generic Enabler (GE) made of a receiver and a replier subcomponents allowing a bidirectional communication between the FIWARE Orion Context Broker (CB) and PySpark. The component works on a low-level socket communication implementing a message passing interface between the two aforementioned counterparts. This interface is equipped with a parser function, hence permitting the creation of both NGSIv2 and NGSI-LD entities ready to use in a custom PySpark algorithm. Once data are preprocessed inside the PySpark evnironment, the component also provide a write-back interface (via REST API) to the Orion CB.


## Why Use Orion PySpark Connector
Orion PySpark Connector was created with the idea of expanding the FIWARE Orion CB's environment to merge with python's one. Python is currently one of the most used programming languages for data analysis, providing lots of scientific libraries for data processing and visualization. Orion, on the other hand, is a powerful tool allowing the management of context elements and sending updates via subscriptions. This connector is able to open a communication path between these two instruments and to combine the advantages they provide at a little-to-none cost.


## Component Architecture
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
[Orion PySpark Connector Usage](docs/quick_start.md)

## Docker
#### This section is still work in progress

The component is available also as a docker image. Useful information on deployment mode are found here: [Roadmap](docs/docker.md)

## Roadmap

Information about the component features to be implemented and current version issues are found here: [Roadmap](docs/roadmap.md)

## License

This software is licensed under [Affero GNU General Public License (GPL) version 3](./LICENSE.txt).


> Please note that software derived as a result of modifying the source code of this software in order to fix a bug or
> incorporate enhancements is considered a derivative work of the product. Software that merely uses or aggregates (i.e.
> links to) an otherwise unmodified version of existing software is not considered a derivative work, and therefore it
> does not need to be released as under the same license, or even released as open source.
