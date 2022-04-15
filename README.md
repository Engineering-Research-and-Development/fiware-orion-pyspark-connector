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


### Replier Side

The orion-pyspark replier is currently a set of tools composed by:
- **`JSON Blueprinter`**: Python 3.8 little program to write a JSON Skeleton for the Replier
- **`Replier Lib`**: Python 3.8 library to import and use in a custom spark job that converts a stream of processed data into a JSON (based on the blueprint generated in with the previous tool) and sends it with a API request.


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
- Modify the `conf.py` file in the repository to set up the IP address and port for both the HTTP Server and the multi-threading socket. **Don't use the same address and port for the HTPP Server and the Sockets**
- Make a subscription to the Orion Broker, inserting the same HTTP server address and port you chose for the configuration file.
- Import all pyspark functions needed for starting the Spark Streaming:
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
The connector will receive data from the orion broker and its bhaviour is based on both the configuration file (if it accepts only body or whole request) and the type of request arrived on the HTTPServer, automatically deciding if the request contains a NGSIv2 or NGSI-LD data. The function above returns both the stream data to be processed (via pyspark mapping) and the streaming context itself.
- Run the streaming context:
```python
# (YOUR ALGORITHM TO PROCESS record)
ssc.start()
ssc.awaitTermination()
```

### Replier

The replier is much more easier to use.  <br />
As mentioned above, to ensure a more user friendly customization, a JSON-Blueprint tool is provided. **This tool is still a prototype and may undergo changes in future versions**. For simpler cases, it works properly.
- Install the requirements for the replier:
```console
pip3 install requests
```
- Modify the `replyconf.py` file to change the JSON Blueprint file path, the API URL and the HTTP method, choosing from "POST", "PUT" and "PATCH". Moreover you need to specify some header fields like the content-type (default application/json) and both fiware service and service_path.
- Generate a JSON Blueprint keeping the following rules **This step is needed only once per JSON format**
   - The generated skeleton will have the following structure: TYPE_OF_FIELD "Fieldname": {} and the replier library knows how to decode it.
   - Select the *String* type to write string
   - Select the *Nested Object* type to open a nested object **That needs to be completed field by field**
   - Select the *Other Field* type to write Integers, Floats, Lists, Dictionaries, Completed Nested "JSONS"
   - The total number of fields inserted (summing every nested field) have to match the total number of values produced by your pyspark algorithm
To launch the Blueprinter, simply run:
```console
python3 JSONBlueprinter.py
```
and follow the instructions of the tool. It will ask for the number of fields of the whole JSON, allowing the customization of the file with nested objects. This tool will generate a *.txt* file with the name provided in the configuration file.
Since the JSON skeleton is the core of this customization, particular attention is reccomended while componing the skeleton.  <br />

- In you pyspark job import the receiver library
```python
import replier_lib as replier
```
- Process the stream of data and send back to the Orion broker using:
```python
response = record.map(lambda x: replier.ReplyToBroker(x))
response.pprint()
```

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
- [ ] Adding NGSI-LD support to Replier **Working On**
- [ ] Tests for NGSI-LD Support for both receiver and replier side.
- [ ] Write a definitive JSON structurer tool



### Medium Term

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
