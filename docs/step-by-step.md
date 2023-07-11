<p align="center">
  <a href="https://www.fiware.org/developers"><img  src="https://fiware.github.io/tutorials.IoT-over-MQTT/img/fiware.png"></a>
</p>

# FIWARE PySpark Connector Step-by-Step Tutorial

This is a step-by-step tutorial on how to configure a working example to try the FIWARE pyspark connector. In this tutorial, we simulate an on-line  residual useful life prediction for batteries. To do so, a machine learning model trained on battery data is deployed as a PySpark algorithm using a spark cluster, while an Orion Context Broker provides data from unseen same-type batteries. This setup allows the real-time prediction of battery residual useful lifes.


## What are PySpark and FIWARE PySpark Connector?

[PySpark](https://spark.apache.org/docs/latest/api/python/) is an open-source distributed computing framework built on Apache Spark, designed for big data processing and analytics. It provides an interface for programming with data stored in distributed systems, such as Hadoop Distributed File System (HDFS) and Apache Cassandra. PySpark enables developers to write data processing tasks in Python, while taking advantage of Spark's powerful capabilities for distributed data processing. It offers a wide range of built-in libraries for handling large-scale data processing tasks, including machine learning, graph processing, and stream processing. PySpark's ability to distribute data and computations across a cluster of machines allows for fast and scalable data processing, making it a popular choice for big data analytics projects.

The **FIWARE PySpark Connector** is a FIWARE Generic Enabler (GE) that facilitates two-way communication between the FIWARE Context Brokers (CB) and PySpark. It consists of two subcomponents, a receiver and a replier, which enable bidirectional data exchange. The connector operates at a low-level socket level, establishing a message passing interface between the CBs and PySpark. This interface includes a parser function, allowing for the creation of NGSIv2 and NGSI-LD entities that can be seamlessly integrated into custom PySpark algorithms. Furthermore, once data is processed within the PySpark environment, the connector offers a write-back interface via a REST API, enabling data to be sent back to the CBs.


## Tutorial Introduction

### Explaining the background scenario

This sci-fi real-world use case is set up in the mineral industry and, in particular, in a cement industry that wants to produce an hi-quality concrete. One of the most important features for a good concrete is the *concrete compressive strength (MPa)*, that is a feature nonlinearly bound with other characteristics, such as the age and the quantity of each ingredents.

This cement industry knew with large times the need of creating a machine learning model to compute the perfect recipe, so they collected a fair amount of recipes experiments in a [dataset](https://www.kaggle.com/datasets/vinayakshanawad/cement-manufacturing-concrete-dataset) (*that's why sci-fi use case*). This dataset encompasses a list of ingredients, expressed as density ($Kg/m^3$), and the age (days) as input features, and the concrete strength (MPa) as output feature.

Having such a dataset, they decided to train a machine learning model, namely a Random Forest Regressor, able to predict the concrete strenght. Training code is available [here](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/tree/step-by-step/tutorial_resources/jobs/Concrete_Training). Once the model is trained, it is ready for inference.

Here, we set up our tutorial: we are providing a service capable of making near-real-time inference on data provided by a context broker. We have our trained model and all we want is to use it to predict concrete strength based on data the industry provides. Focus was mainly put on the interaction between Orion and PySpark (where the inference algorithm runs), hence in explaining how the *fiware-pyspark-connector* can be used to make this interaction possible.

Therefore, this tutorial **is NOT covering**
- Data Ingestion through Agents
- Data Pipelines. In short, the training and prediction algorithms are tuned to work well together and data are considered already clean
- Data Visualization


### Preparing the toolkit

This tutorial needs few tools to be up and running.

First of all, the following components are suggested to speed up operations:
- [Postman](https://www.postman.com/)
  - Postman can be installed by running the executable on Windows and using snap on Linux: `sudo snap install postman`
  - It is useful to make requests to the context broker without using curl.
  - *Strongly* suggested
- [Robo 3T](https://robomongo.org/)
  - In the same way, Robo 3T can be installed on linux using the command `sudo snap install robo3t-snap`
  - It is useful to rapidly explore and query mongo, but it is not so strongly suggested as postman


Then, in the [**tutorial_resources**](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/tree/step-by-step/tutorial_resources) folder, it is possible to find some necessary tools to set up our working inference environment.

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
      - Other libraries can be installed on need, as explained in the [Docker](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/step-by-step/docs/docker.md) section of this repository.
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
    - Map function contains the custom processing function
  - Result is returned as RDD.
  - If needed, other processing steps can be done
 
- **Fourth Phase: Data Write-back**
  - Spark driver calls the *forEachRDD* function, then passes each rdd to the *forEachPartition* function, hence mapping the last result to a worker
    - using *forEachRDD* is used as RDD sink (since pyspark is lazy, all operations are performed only when a sink operation is performed)
    - using *forEachPartition* allow to set up connector parameters only once, then it iterates on incoming RDDs
    - *forEachPartition* needs a callback function that uses an iterator as argument
  - Connector sends a POST/PATCH/PUT request to orion
  - Connector shows Orion response


