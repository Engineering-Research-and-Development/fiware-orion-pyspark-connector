## Usage

### Receiver

Once installed the requirements, it is possible to use the connector by following these steps:
- Import the connector library and all PySpark functions needed for starting the Spark Streaming:
```python
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark import StorageLevel
from FPC import connector
```
- The connector is configured with default values. If needed, manually configure the connector using the **RECV_SINGLETON** instance of the replier configurer class:
```python
connector.RECV_SINGLETON.http_address = # The machine IP address / Docker container IP if running in docker
connector.RECV_SINGLETON.http_port = # Desired Port
connector.RECV_SINGLETON.socket_address = # localhost is fair enough / Docker container IP if running in docker
connector.RECV_SINGLETON.socket_port = # Desired port
connector.RECV_SINGLETON.request_completeness = # True if full HTTP packet is needed / False if only body strings are needed
connector.RECV_SINGLETON.socket_buffer = # 2048 by default, use more if needed
connector.RECV_SINGLETON.max_concurrent_connections = # 20 suggested by default, use more if needed. 
```
**WARNING: Don't use the same (address, port) couple for the HTPP Server and the Sockets**
**WARNING: Remember that the number of EFFECTIVE_CONCURRENT CONNECTIONS = (MAX_CONCURRENT_CONNECTIONS - 1) since 1 connection is reserved by the pyspark socket.**
  
- Make a subscription in the Context Broker, inserting the same HTTP server address and port you chose for the configuration file.

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
The connector will receive data from the broker and its bhaviour is based on both the configuration file (if it accepts only body or whole request) and the type of request arrived on the HTTPServer, automatically deciding if the request contains a NGSIv2 or NGSI-LD data. The function above returns both the stream data to be processed (via PySpark mapping) and the streaming context itself. Please, refer to NGSIv2 or NGSI-LD base classes in the `connectorconf.py` file to understand their structure.

- Run the streaming context, like the example below:
```python

def MyProcessFunction:
   # (YOUR ALGORITHM TO PROCESS record)
   return result
   
'''
Processing steps:
   - Flattening entity list from event
   - For each entity, takes 'someAttribute' and process its value with the previously defined function
'''
processed_record = record.flatMap(lambda x: x.entities).map(lambda x : MyProcessFunction(x.attrs['someAttribute].value))

# Sink the result to trigger mapping
processed_record.pprint()

# Start the above workflow until termination
ssc.start()
ssc.awaitTermination()
```

### Replier


- In you PySpark job import the connector library and set up your configuration by accessing the singleton instance of the replier configuration class, i.e:
```python
from FPC import connector

connector.REPL_SINGLETON.api_url = # Insert a valid CB API URL
connector.REPL_SINGLETON.api_method = # Choose among "POST" "PUT" "PATCH"
connector.REPL_SINGLETON.fiware_service = # Fiware-Service Header for HTTP Requests
connector.REPL_SINGLETON.fiware_servicepath = # Fiware-ServicePath Header for HTTP Requests
connector.REPL_SINGLETON.content_type = # Default set to "application/json; charset=utf-8"
# Here there are complex requests configuration, see below for further details
connector.REPL_SINGLETON.blueprint_file = # Relative path to a blueprint file for complex requests
connector.REPL_SINGLETON.placeholder_string # Placeholder string for complex requests
```
- **The replier can be used in three different modes: structured, unstructured and semi-structured.**

- *Structured mode*:
   - Create a .txt file with the wanted request body, using the placeholder string decided in the configuration file every time a field has to be completed by the output of the PySpark algorithm
   - If the algorithm produces more than one value, make sure that the incoming values are ordered with respect to the wanted fields
   - Take in account that this method is slower than the others (since files are read from disk) and it fits well when completing large bodies
   - Use the ReplyToBroker function passing the values from the algorithm
```python
response = record.map(lambda x: connector.ReplyToBroker(x))
response.pprint()
```

- *Semi-structured mode*: 
   - Use the SemistructuredReplyToBroker function passing both values and request body with placeholders decided in the configuration file
   - If the algorithm produces more than one value, make sure that the incoming values are ordered with respect to the body fields
   - This method is faster than the structured one, but it fits for small request bodies
   - In case of JSON bodies, remember that properties and string fields must be enclosed in double quotes, so the whole body should be enclosed in single quotes like in the following example (i.e: the replace string configured is %%PLACEHOLDER%%):
```python
response = record.map(lambda x: connector.SemistructuredReplyToBroker(x, '{"example" : %%PLACEHOLDER%% }'))
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
response = record.map(lambda x: connector.UnstructuredReplyToBroker('{"price" :' + str(x.attrs["price"].value) +' }'))
response.pprint()
```


### Subscription Tool

The subscribing tool is an optional tool capable of making easy subscription to the context broker. It provides a API allowing to browse the entity space in the context broker, select one of them and then selecting the attributes to return in the subscription.

**Currently, conditions are not implemented. Subscriptions with condition will be implemented later**

- To use the subscribing tool, import it with the following line of code:
```python
from FPC import subscribing_tool as sub
```
**Remember: the subscription tool will use the same configuration of the connector. If needed, configure both the receiver and replier side**
```python
sub.RECV_SINGLETON.http_address = # The machine IP address / Docker container IP if running in docker
sub.RECV_SINGLETON.http_port = # Desired Port
sub.REPL_SINGLETON.fiware_service = # Fiware-Service Header for HTTP Requests
sub.REPL_SINGLETON.fiware_servicepath = # Fiware-ServicePath Header for HTTP Requests
```

- Use the following function, keeping in mind that:
   - base_url: is the base url of the context broker. Usually, it would be: "http://ipaddress:port/v2/" or "http://ipaddress:port/ngsi-ld/v1/"
```python
sub.SubscribeToEntity(base_url)
```

- The algorithm will browse the base url, showing a list of the currently existing entities.
- Select an entity among the existing ones by typing the name (case insensitive)
- The algorithm will show a numbered list of attributes 
- Type the attribute number to add it into a list of selected attributes for the subscription
   - Type >QUIT to exit the selection list
   - Type >ALL to copy the whole list and exit the selection
- Now type the attribute number to add it into a list of condition attributes for the subscription (v2 Only)
   - Type >QUIT to exit the selection list if at least an attribute is selected
   - Type >ALL or >QUIT if no attribute is selected to copy the whole list and exit the selection
- Type the description you want to put
- If the algorithm succeeds, it will show the success message and the subscription is posted on the context broker
