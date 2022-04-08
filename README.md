# fiware-orion-pyspark-connector


## Table of Contents

-   [What is this connector](#what-is-this-connector)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage](#usage)
-   [Maintainers](#maintainers)
-   [Roadmap](#roadmap)
-   [License](#license)


## What is this connector

The orion-pyspark connector is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a pyspark job.
The tool is represented in the following diagram and it is made of:


![Connector-diagram](https://user-images.githubusercontent.com/103200695/162405802-3bc222df-63aa-41d9-a347-3c270d8ab8a4.png)


-   **`Connector Library & NGSI classes`**: Set of functions and class definition for NGSI Events
-   **`Connector start`**: Python 3.8 code to start the connector.
-   **`* Primers (OPTIONAL)`**: Python 3.8 code to implement in a pyspark job to obtain a stream of NGSI Event objects



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
**N.B:** in the requirement file pyspark is omitted since it is assumed that this library is already installed. If pyspark is needed, use the following guide:

[Install pySpark](https://towardsdatascience.com/installing-pyspark-with-java-8-on-ubuntu-18-04-6a9dea915b5b)ù


## Usage

Once installed the requirements, the connector is easy to use:
- Load files on the same machine running the spark job
- Modify the `conf.py` file in the repository to set up the IP address and port for both the HTTP Server and the multi-threading socket. **Don't use the same address and port for the HTPP Server and the Socket Server**
- Make a subscription to the Orion Broker, inserting the HTTP server address and port
- Run the connector using ```console
python3 connector_start.py
```

