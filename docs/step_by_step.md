<p align="center">
  <a href="https://www.fiware.org/developers"><img  src="https://fiware.github.io/tutorials.IoT-over-MQTT/img/fiware.png"></a>
</p>

# FIWARE PySpark Connector Step-by-Step Tutorial

This is a step-by-step tutorial on how to configure a working example to try the FIWARE pyspark connector. In this tutorial, we simulate an on-line  residual useful life prediction for batteries. To do so, a machine learning model trained on battery data is deployed as a PySpark algorithm using a spark cluster, while an Orion Context Broker provides data from unseen same-type batteries. This setup allows the real-time prediction of battery residual useful lifes.

**TUTORIAL STATUS: UPDATED TO LAST VERSION**

## What are PySpark and FIWARE PySpark Connector?

[PySpark](https://spark.apache.org/docs/latest/api/python/) is an open-source distributed computing framework built on Apache Spark, designed for big data processing and analytics. It provides an interface for programming with data stored in distributed systems, such as Hadoop Distributed File System (HDFS) and Apache Cassandra. PySpark enables developers to write data processing tasks in Python, while taking advantage of Spark's powerful capabilities for distributed data processing. It offers a wide range of built-in libraries for handling large-scale data processing tasks, including machine learning, graph processing, and stream processing. PySpark's ability to distribute data and computations across a cluster of machines allows for fast and scalable data processing, making it a popular choice for big data analytics projects.

The **FIWARE PySpark Connector** is a FIWARE Generic Enabler (GE) that facilitates two-way communication between the FIWARE Context Brokers (CB) and PySpark. It consists of two subcomponents, a receiver and a replier, which enable bidirectional data exchange. The connector operates at a low-level socket level, establishing a message passing interface between the CBs and PySpark. This interface includes a parser function, allowing for the creation of NGSIv2 and NGSI-LD entities that can be seamlessly integrated into custom PySpark algorithms. Furthermore, once data is processed within the PySpark environment, the connector offers a write-back interface via a REST API, enabling data to be sent back to the CBs.



## Architecture

<p align="center">
  <img  src="https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/2a975b11-60d7-43a4-b6f9-626f8a1ef273">
</p>

The above figure explains the overall architecture set up in the tutorial and how each component communicate with the others. In particular, it is possible to see that the context broker sends data to the driver machine, while workers are in charge to write back computation results (if any). In this scheme, we set up fixed ip addresses (using docker network) in order to speed up tutorial setup. Shown IPs, however, are not mandatory: it is possible to get any machine IPs and use that when configuring the connector.


### How the FIWARE PySpark Connector Works

The mechanism behind the pyspark connector is quite simple: it sets up a simple HTTP server to receive notifications from Orion and then pushes it inside PySpark using the [SocketTextStream](https://spark.apache.org/docs/3.1.1/api/python/reference/api/pyspark.streaming.StreamingContext.socketTextStream.html) function that creates an input TCP source for building *Resilient Distributed Datasets* (RDDs), the streaming data unit of pyspark. 
The figure below shows the detailed process of connector setup, followed by data reception, management, processing and sinking.

![SequenceDiagram](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/1e2618d4-6641-4ced-b412-305c1db4bff0)

- **First Phase: Setup (or handshaking)**
  - (PRE) A PySpark session is already started
  - Function *Prime* from fiware pyspark connector is called.
    - Connector's HTTP server starts in sleeping phase
    - Connector's Multi-Thread Socket Server (MTSS) starts, remaining in listening phase
    - Spark Streaming context is initialized
    - pyspark's SocketTextStream function creates a TCP input with any available local IPs and Port, connecting to MTSS
    - MTSS saves pyspark's TCP socket as "first client"
    - MTSS awakens HTTP Server
  - Streaming Context and RDD channel are returned

- **Second Phase: Data Reception**
  - (PRE) Connector's HTTP Server is subscribed to Orion for an entity  
  - (PRE) An attribute of the [subscribed](https://github.com/FIWARE/tutorials.Subscriptions) entity changed
  - Orion sends a notification to Connector's HTTP Server
  - HTTP Server structures the incoming HTTP packet into a string message
  - HTTP Server open a random socket and sends incoming message to MTSS's central socket
  - MTSS's central socket receive the message and opens a new Thread to handle this connection
  - MTSS's turns the message to PySpark SocketTextStream
  - PySpark maps the incoming message to a worker machine
    - PySpark worker parses string message in a NGSIEvent object
  - NGSIEvent is now available as RDD
   
- **Third Phase: Data Processing**
  - Spark driver maps the RDD contaning NGSIEvent object to a worker
    - Map function uses a custom processing function, taking an RDD as input and returning custom function's output as "mapped" RDD
  - Result is returned as RDD.
  - If needed, other processing steps can be done
 
- **Fourth Phase: Data Write-back**
  - Spark driver calls the *forEachRDD* function, then passes each rdd to the *forEachPartition* function, hence mapping the last result to a worker
    - using *forEachRDD* is used as RDD sink (since pyspark is lazy, all operations are performed only when a sink operation is performed)
    - using *forEachPartition* allow to set up connector parameters only once, then it iterates on incoming RDDs
    - *forEachPartition* needs a callback function that uses an iterator as argument
  - Spark driver sinks the data flux, mapping to worker an output function
  - Connector sends a POST/PATCH/PUT request to orion
  - Connector shows Orion response


## Deploying the provided material

### Explaining the background scenario

This sci-fi real-world use case is set up in the mineral industry and, in particular, in a cement industry that wants to produce an hi-quality concrete. One of the most important features for a good concrete is the *concrete compressive strength (MPa)*, that is a feature nonlinearly bound with other characteristics, such as the age and the quantity of each ingredents.

This cement industry knew with large times the need of creating a machine learning model to compute the perfect recipe, so they collected a fair amount of recipes experiments in a [dataset](https://www.kaggle.com/datasets/vinayakshanawad/cement-manufacturing-concrete-dataset) (*that's why sci-fi use case*). This dataset encompasses a list of ingredients, expressed as density ($Kg/m^3$), and the age (days) as input features, and the concrete strength (MPa) as output feature.

Having such a dataset, they decided to train a machine learning model, namely a Random Forest Regressor, able to predict the concrete strenght. Training code is available [here](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/tree/main/tutorial_resources/jobs/Concrete_Training). Once the model is trained, it is ready for inference.

Here, we set up our tutorial: we are providing a service capable of making near-real-time inference on data provided by a context broker. We have our trained model and all we want is to use it to predict concrete strength based on data the industry provides. Focus was mainly put on the interaction between Orion and PySpark (where the inference algorithm runs), hence in explaining how the *fiware-pyspark-connector* can be used to make this interaction possible.

Therefore, this tutorial **is NOT covering**
- Data Ingestion through Agents
- Data Pipelines. In short, the training and prediction algorithms are tuned to work well together and data are considered already clean
- Data Visualization


### Preparing the toolkit

This tutorial needs few tools to be up and running.

The first tool it is necessary to install [Docker](https://docs.docker.com/engine/install/) with [docker-compose](https://docs.docker.com/compose/). They are both mandatory tools to run the tutorial.

Then, to speed up operations, the following components are also suggested:
- [Postman](https://www.postman.com/)
  - Postman can be installed by running the executable on Windows and using snap on Linux: `sudo snap install postman`
  - It is useful to make requests to the context broker without using curl.
  - *Strongly* suggested
- [Robo 3T](https://robomongo.org/)
  - In the same way, Robo 3T can be installed on linux using the command `sudo snap install robo3t-snap`
  - It is useful to rapidly explore and query mongo, but it is not so strongly suggested as postman


Finally, in the [**tutorial_resources**](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/tree/main/tutorial_resources) folder, it is possible to find the resources to set up our working inference environment.

- The first thing is a **docker-compose** containing the necessary FIWARE/Apache components:
  - A *Spark Cluster* with a master node and two workers, containing the following python libraries and their dependencies:
      - numpy
      - scipy
      - simpy
      - pandas
      - scikit-learn
      - matplotlib
      - seaborn
      - *pyspark*
      - ***fiware-pyspark-connector***
      - Other libraries can be installed on need, as explained in the [Docker](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/main/docs/docker.md) section of this repository.
  - The [*Orion Context Broker*](https://fiware-orion.readthedocs.io/en/master/)
  - A *MongoDB* database (for Orion)

- Second, the **"Jobs"** Folder. In this folder there are:
  - The *Concrete_Training* folder , containing:
    - a minimal source code used for training (for curious, data exploration phase is offline)
    - the .csv dataset
  - The *Concrete_Prediction* folder, with:
    - the inference source code, the one that is explained in the next sections
    - the .csv dataset
  
- Finally, a **Postman Repository** with all the necessary API to get ready.


### Get Started!

- First step to get started is to download the tutorial resource folder on your machine. It is possible to do it by using the github download zip function or cloning the repository via: 
```git clone https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector.git```
- Browse the newly downloaded folfer and search tutorial_resources one. Open the terminal in this folder, then use docker-compose to start the environment.
```docker compose up -d```
- While images are pulling and containers are building, open Postman and import the tutorial collection findable in the same folder containing the docker-compose. In the upper right part of the postman window it is possible to find an "import" button, click it and then select the *FIWARE Pyspark Connector tutorial collection.postman_collection.json* file.
![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/867a7662-0261-4d21-8a03-d5906317998b)
- Once the collection is imported, check if Orion is up by using the **Get Data Entity** API.
  - Notice in the below figure that all collection's API contains both the **FIWARE-SERVICE** and **FIWARE-SERVICEPATH** headers set.
![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/ad577be6-b245-4eda-a9c4-48e840338f81)
- If you get a positive response status (200 OK), then orion is ready.
- Open the **Create Data Entity** API and send it. It will create the entity where inputs and outputs are stored. In particular
  - All ingredent quantity / age features are inputs
  - "strength" attribyute will be used as input for this tutorial. It is the ground truth variable, used to compute the prediction error
  - "predicted_strength" attribute and "prediction_error" attributes will be used to store the outputs of our prediction algorithm
- Once the entity is created, it is possible to start the prediction algorithm. Open a new terminal and type:
```cmd
docker exec -it pyspark_master bash
# Now all commands are run inside the container
cd ./data/Concrete_Prediction
spark-submit predict.py --py-files model.pickle
```
- The following terminal strings indicate that connector is up and running:
![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/9c58d901-1e72-4c7c-b8ca-1f27573276a2)
- Pick the ip and port of the HTTP endpoint (in image above, 172.28.1.1 and  8061)
- Return in postman and search for **Connector Subscription** API.
- Under notification, change the url using the same IP and port previously displayed
![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/2848cd37-7a8e-442d-abab-bb99c568f799)
- Send the API to Orion.
- To obtain a prediction, now, it is only necessary to change some values in the entity. Use the **Test Prediction** API changing some values. You can both use random values or search for a valid input in the dataset contained in *"jobs/Concrete_Training/concrete_dataset.csv"* file.
- After updating the entity, the spark job should print some lines such as:
![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/841747ac-f5aa-4a6f-9887-85a0a41664e0)

Until now, we just explained how FIWARE PySpark connector works, after being correctly configured and used. Next part of this tutorial provides deeper comprehension of what it is necessary to do with custom algorithms to achieve those results.


## How to Develop an NGSI-Integrated Custom Algorithm with FIWARE PySpark Connector

### Configuration
To start getting familiar with FIWARE pyspark connector, let's speak of its configuration file.
Configuration file contains some class definition and default configuration values. Here's an example: 

![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/41d2c7f0-c0d8-4b7b-a7fe-b06292182221)
(figure above may be dated and may not correspond to latest version of the connector)

The above figure displays the Replier configuration class. It contains the following values:
- *http_address:* IP of the HTTP server, defaultly set to host's IP
- *http_port:* port of the HTTP server, defaultly set to 8061
- *socket_address:* IP address of the main socket in the Multi-Thread Socket Server, default value is'localhost'
- *socket_port:* = port of the main socket in the Multi-Thread Socket Server, default value is 9998
- *request_completeness:* setting to abilitate parsing functionalities to convert the incoming HTTP request in NGSIEvent Object, otherwise they are treated as strings. Default value is True
- *socket_buffer:* value that sets how large are messages exchanged in the MTSS. Default value is 2048, usually it is suitable for most cases
- *max_concurrent_connections:* value setting how many concurrent connections are allowed by MTSS. Default value is 20

![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/0d7c38cd-98cc-4877-8e14-ee5ea0202f8b)
(figure above may be dated and may not correspond to latest version of the connector)


This one, instead, is the Replier configuragion class. It contains the following attributes:
- *fiware_service:* value for the "Fiware-Service" header for an HTTP request [see above](#get-started)
- *fiware_servicepath:* value corresponding to the "Fiware-ServicePath" header of the HTTP Request
- *content_type:* attribute expressing content type for request. Default value is "application/json; charset=utf-8"
- *blueprint_file:* name of a "skeleton" request file to be completed with processed values. Useful for complex requests.
- *placeholder_string:* attribute containing a placeholder string that will be replaced with processed values. It can be used in combination with the blueprint file to easily build POST/PUT/PATCH requests to Orion

It is useful to know the configuration file since it contains both values usually not worthy to be changed (i.e.: socket buffer) but also values that may be changed runtime, if necessary. This configuration mechanism, in fact, allow an easy set up of the connector without worrying too much about some technical issues, but also allow a user to change configuration runtime. It is also useful to take in account that the environment in which the connector works is a spark cluster. This means that default configuration values are correctly held by both master (driver) and workers, however any change of configuration attributes during execution may not be consistent throughout the cluster. Usually, the *Replier* configuration runs only on driver, meaning that it is not necessary to worry about propagating new values into workers. However, since replier configuration is mainly used by workers, it will be necessary to change values only in functions.

Moreover, configuration files contains base classes used for parsing raw HTTP Requests into object. Knowing how classes are structured helps using NGSI Entity Objects to manipulate data.
The below diagram is a scheme showing how classes are linked together:
![image](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/c50ca52c-419d-4789-8d64-f99ed7b4ea12)



### Building an integrated algorithm

This subsection wants to dive inside the code contained in [**predict.py**](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/main/tutorial_resources/jobs/Concrete_Prediction/predict.py) to understand how to integrate your custom algorithm with the FIWARE PySpark connector.

- **Step 1: Start a Spark Session**
  
First and foremost, to use pyspark it is important to import PySpark libraries, the FIWARE PySpark Connector library and create or get a spark session to use:

```python
from fpc import connector

from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf, StorageLevel
```

Once getting the spark session, giving a name to the application and connecting to a master node (in this case local machine), we link the session to the *spark* variable, hence we are able to obtain the sparkContext which is the connection to the Spark Cluster that allows the creation of RDDs.

- **Step 2 (Optional): Configure the Receiver**

Using few lines of code, it is possible to set any value for the receiver configuration. In this case, we are forcing the connector to use the docker container IP and use the port. Since default configuration file should have given the same results, this step was reported only for demonstration purpose. Usually, receiver configuration works well for any machine. However, should it be necessary to use another IP, it is possible.
```python
###### CONNECTOR CONFIGURATION FOR MASTER - BEFORE STARTING #######
connector.RECV_SINGLETON.http_address = "172.28.1.1"
connector.RECV_SINGLETON.http_port = 8061
###########################################
```

**Step 3: Implement Data Mapping in Data Preparation Function**

A data preparation function is structured like the following one:
```python
def PrepareData(entity):
    '''
    Function to prepare data for prediction.
    It was adapted to prepare data from an NGSI Entity
    '''
    
    ###### Lines of code necessary to pick attributes from an NGSI Entity and build a dataframe #####
    # Picking values from OCB, converting into "horizontal" numpy array
    values = np.array([val.value for val in entity.attrs.values()]).reshape(1, -1)
    # Creating a pandas dataframe to speed up data preparation
    df = pd.DataFrame(values, columns=list(entity.attrs.keys()))
    #################################################################################################
    # Dropping target column and taking prediction single value
    x = df.drop('strength', axis=1).to_numpy().reshape(1,-1)
    y = df['strength'].to_numpy()
    return x, y
```
It takes a NGSIEntity (v2) from an NGSI Event and extracts its attributes to build a data unit to be processed by the model. Notice that, since the subscription has not included the output attributes, it was only necessary to separate input features (ingredients, age) and strength in x and y values. Hence, it is only sufficient to add some line of code to map data, then you can re-use every data cleaning / transformation / quality check implemented before.

**Step 4: Reuse your prediction function**

As shown below, this function is a quite agnostic prediction function. It simply loads a model, predicts an output based on inputs, then uses the ground truth to compute the mean absolute error. Since data were mapped before, it is not necessary to add lines of code in this part.

```python
def PredictAndComputeError(x, y):
    # Function already built to predict data, left as is.
    
    prediction = loaded_model.predict(x)[0]
    # Computing absolute error between ground truth and predicted value
    MAE = np.abs(y - prediction)
    return prediction, MAE
```

**Step 5: Define Worker Mapping in PySpark**

Now is necessary to define some mapping functions to work with RDDs. This is the most tricky part of all FIWARE PySpark Connecto integration and it will be explained point by point.

```python
try:
    event, ssc = connector.Prime(sc, 1 , StorageLevel.MEMORY_AND_DISK_2)
    entity = event.flatMap(lambda x: x.entities)
    entity.foreachRDD(lambda rdd: rdd.foreachPartition(InjectAndPredict))
except Exception as e:
    print(e)

# Run until killed
ssc.start()
ssc.awaitTermination()
```

- First of all, we are in the try-catch block. Here it is necessary to start the [Spark Streaming Context](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.streaming.StreamingContext.html) This is done thanks the *Prime* function in connector's library. This function requires three arguments, which are the spark context, the duration (in seconds) of the receiving window, and a [Storage Level](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.StorageLevel.html) in which data are stored during execution. Check the link for the list of possible storage levels and their meaning. Since PySpark streaming is based on the concept of DStreams (Discretized Streams), that are continuous RDDs of the same type catched and processed within a time window, we setup the connector to process those data every x seconds. The *Prime* function returns the DStream channel of NGSIEvents and the streaming context itself, created inside the connector. Those two objects are used in later steps.
- Since we don't know how many events are catched in a second and how many entities are contained in each NGSIEvent, we flatten the DStream channel to be a list of entities captured in the time window defined before. In this way, we are able to capture each entity update, passing from an "Event Context" to the Entity itself.
- For each RDD contained in the result of the *FlatMap* function (so each entity) we sink our data. PySpark Streaming is defined *lazy*, meaning that all operations are performed only when data are sunk. Some ways to sink data are the *foreachRDD* function or the *pprint* one. The first function is able to map RDDs to workers and perform operations, while pprint only sinks data showing them to terminal. Each RDD is processed by *foreachPartition* that requires a callback function, in this case named *InjectAndPredict* (it is shown in the following step).
- Once defined the flow of data (it can be even more complex), the streaming context is started and will process data until termination.


**Step 6: Callback Function Definition**

Last, but not least, it is necessary to define the *foreachPartition*'s callback function: *InjectAndPredict*. This function is the "control point" of the entities coming from the previous step and performs all operations sinking the PySpark stream.

```python
def InjectAndPredict(iter):
    # Function injected into workers to work on RDDs
    
    ###### CONNECTOR CONFIGURATION INJECTION #######
    connector.REPL_SINGLETON.fiware_service = "tutorial"
    connector.REPL_SINGLETON.fiware_servicepath = "/pyspark"
    connector.REPL_SINGLETON.placeholder_string = "%%PLACEHOLDER%%"
    ###########################################

    # Iterating over entities (coming from flatmap)
    for entity in iter:
        
        x, y = PrepareData(entity)
        prediction, MAE = PredictAndComputeError(x, y)

        # Preparing body for request, sending to CB
        body = '''{"predicted_strength": {"value": %%PLACEHOLDER%% }, "prediction_error" : {"value": %%PLACEHOLDER%% }}'''
        response = connector.SemistructuredReplyToBroker([prediction, MAE], body, "http://172.28.2.1:1026/v2/entities/Concrete/attrs/", "PATCH")
        print(response)
    return response
```

The use of the *foreachPartition* function is related to the setup of a connection. It is an efficient function that maps RDD partitions to workers, moreover it is also suggested as best practice when enstablishing connections. In this case we are making only REST calls to the context brokers, however if needed, you can integrate FIWARE PySpark Connector with other systems that may require a connection. In the first part of this function, we define the Replier's configuration. Since workers are different machines, it is necessary to explicitly define those configuration inside the mapped function. In this case, we have changed the *Fiware-Service* and *Fiware-ServicePath* headers, moreover we also defined a different placeholder String.

Then, each RDD is processed by the iterator inside. We prepare data and make our predictions as explained above. In the end, we prepare a simple body skeleton to populate with our results and use the *SemistructuredReplyToBroker* replier function (explained [here](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/main/docs/quick_start.md#replier)) to update orion.

Well done, we have closed the loop!


## Summary and Conclusion

The above tutorial explained:
- Some PySpark concepts
- How to deploy a minimal application using the FIWARE PySpark Connector through docker
- The architecture of the FIWARE PySpark Connector and how data flow into it
- How to integrate a custom near-realtime algorithm with Orion trhough the FIWARE PySpark Connector

The FIWARE PySpark Connector is currently under development. New features can be added, other may become deprecated and/or deleted. This means that it may happen that some figures are not updated every time. Check the above status to ensure the tutorial is aligned with the last version.
Please, use the [Issues](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/issues) or the [StackOverflow](https://stackoverflow.com/questions/tagged/fiware+orion+pyspark) channel to ask for help or suggest new features!
