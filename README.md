# FIWARE Orion pyspark connector


## Table of Contents

-   [What is this connector](#what-is-this-connector)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage](#usage)
-   [Actual Version Limits](#actual-version-limits)
-   [Roadmap](#roadmap)
-   [License](#license)


## What is this connector

### Receiver Side

The orion-pyspark receiver is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a pyspark job.
The tool is represented in the following diagram and it is made of:


![Connector-diagram drawio](https://user-images.githubusercontent.com/103200695/162898368-dc378146-4705-42ec-a4d5-98220ece0382.png)


-   **`Connector Library & NGSI classes`**: Set of functions and class definition for NGSI Events
-   **`Connector start`**: Python 3.8 code to start the connector.
-   **`Primers (OPTIONAL)`**: Python 3.8 pyspark streaming to implement in an own pyspark job to obtain a stream of NGSI Event objects



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

Once installed the requirements, the connector is easy to use:
- Load files on the same machine running the spark job
- Modify the `conf.py` file in the repository to set up the IP address and port for both the HTTP Server and the multi-threading socket. **Don't use the same address and port for the HTPP Server and the Sockets**
- Make a subscription to the Orion Broker, inserting the same HTTP server address and port you chose for the configuration file.
- Run the connector using 
```console
python3 connector_start.py
```
Alternatively, you can import the connector start using the following importing line:
```python
import connector_start
```

- Import all pyspark functions needed for starting the Spark Streaming:
```python
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark import StorageLevel
import conf as connectorconf #This is the configuration file
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
- Start a StreamingContext , passing the SparkContext and the number of second of your sliding window
```python
ssc = StreamingContext(sc, YOUR_NSECONDS)
```
- In the end, you can start your SocketTextStream
```python
record = ssc.socketTextStream(connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT, storageLevel=StorageLevel.MEMORY_AND_DISK_2)
```

The previous steps are implemented in the optional snipped of code which allow you also the conversion from a JSON format to the NGSI Events
To obtain a stream of NGSI Events:
- **Optional** modify the `{}_primer.py` file to set up the spark configuration
- **Optional** import the `{}_primer.py` file (where {} indicates the name prefix of the file, i.e: NGSIV2) in your custom spark job and save both the event stream and the stream socket with the following code:

```python
import {}_primer as NGSI
event, ssc = NGSI.Prime()
#event variable contains the parsed stream, ssc is the stream itself. 
#Apply the pyspark algorithm on the event variable, then run the stream using ssc.run()
```

## Actual Version Limits

It is important to underline that currently this connector support a single-input single-output connection, limiting to **1** the number of supported spark job per connector. To implement multiple connectors, it is necessary to run another spark job with different addresses.  <br />
It is strongly reccomended to use this connector in local: a future version implementing security will be provided


## Roadmap

### Short Term

- ~~Adding a Sink to write back to the broker.~~
- Efficiency improvements
- Find an elegant way to keep Spark socket in memory
- Better Socket management (automatic ports)


### Medium Term

- Adding NGSI-LD support
- Subscribing tool
- Evolving this "SISO" connector in a "MIMO" one to support multiple spark jobs

### Long Term
- Adding security to connections


## License

This software is licensed under [Affero GNU General Public License (GPL) version 3](./LICENSE.txt).


> Please note that software derived as a result of modifying the source code of this software in order to fix a bug or
> incorporate enhancements is considered a derivative work of the product. Software that merely uses or aggregates (i.e.
> links to) an otherwise unmodified version of existing software is not considered a derivative work, and therefore it
> does not need to be released as under the same license, or even released as open source.
