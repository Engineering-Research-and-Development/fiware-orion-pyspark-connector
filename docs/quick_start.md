## Usage

### Receiver

Once installed the requirements, it is possible to use the connector by following these steps:
- Load files on the same machine running the spark job
- Modify the `connectorconf.py` file in the repository to set up the IP address and port for both the HTTP Server and the multi-threading socket. 
   - If your PySpark job is running in a docker container, make sure that both the server and multi-thread socket *IP addresses* are the same of that container
   - **Don't use the same (address, port) couple for the HTPP Server and the Sockets**
   -  Currently, the user has to make sure that the chosen ports are free. In future versions, automatic port setting is evaluated for the multi-thread socket.
   -  The "REQUEST_COMPLETENESS" field in this file allow the user to choose if obtain a raw body (JSON Format) or the whole request (with HTTP Headers) to work with a NGSIEvent Object
   -  The SOCKET_BUFFER field allow the user to increment the socket buffer to match his needs.
   -  The MAX_CONCURRENT_CONNECTIONS field allow the user to set the maximum concurrent connections of the main socket. It is suggested to keep this number sufficiently high. **Please, remember that the number of effective concurrent connections is MAX_CONCURRENT_CONNECTIONS - 1 since 1 connection is reserved by the pyspark socket.**
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
record, streamingcontext = connector.Prime(sc, YOUR-DESIRED-NUMBER-OF-SECONDS, StorageLevel.MEMORY_AND_DISK_2)
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
