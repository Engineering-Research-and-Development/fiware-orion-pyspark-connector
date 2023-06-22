<p align="center">
  <a href="https://www.fiware.org/developers"><img  src="https://fiware.github.io/tutorials.IoT-over-MQTT/img/fiware.png"></a>
</p>

## FIWARE PySpark Connector Step-by-Step Tutorial

This is a step-by-step tutorial on how to configure a working example to try the FIWARE pyspark connector. In this tutorial, we simulate an on-line  residual useful life prediction for batteries. To do so, a machine learning model trained on battery data is deployed as a PySpark algorithm using a spark cluster, while an Orion Context Broker provides data from unseen same-type batteries. This setup allows the real-time prediction of battery residual useful lifes.


### What are PySpark and FIWARE PySpark Connector?

[PySpark](https://spark.apache.org/docs/latest/api/python/) is an open-source distributed computing framework built on Apache Spark, designed for big data processing and analytics. It provides an interface for programming with data stored in distributed systems, such as Hadoop Distributed File System (HDFS) and Apache Cassandra. PySpark enables developers to write data processing tasks in Python, while taking advantage of Spark's powerful capabilities for distributed data processing. It offers a wide range of built-in libraries for handling large-scale data processing tasks, including machine learning, graph processing, and stream processing. PySpark's ability to distribute data and computations across a cluster of machines allows for fast and scalable data processing, making it a popular choice for big data analytics projects.

**FIWARE PySpark Connector** is a library component leveraging the low-level PySpark API and Resilient Distributed Datasets to receive HTTP notification from a context broker and map them to working nodes executing Python code.


In this tutorial, the chosen context broker is [Orion](https://fiware-orion.readthedocs.io/en/master/).
