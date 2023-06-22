<p align="center">
  <a href="https://www.fiware.org/developers"><img  src="https://fiware.github.io/tutorials.IoT-over-MQTT/img/fiware.png"></a>
</p>

## FIWARE PySpark Connector Step-by-Step Tutorial

This is a step-by-step tutorial on how to configure a working example to try the FIWARE pyspark connector. In this tutorial, we simulate an on-line  residual useful life prediction for batteries. To do so, a machine learning model trained on battery data is deployed as a PySpark algorithm using a spark cluster, while Orion Context Broker provide data from unseen same-type batteries. This setup allow the real-time prediction of batterie's residual useful life.


### What are PySpark and FIWARE PySpark Connector?

[PySpark](https://spark.apache.org/docs/latest/api/python/) is the Python API for Apache Spark. It provides a wide range of Spark's features, such as SparkSQL, SparkMLLib, Dataframes, leveraging the Python language environment which is really popular in data science. **FIWARE PySpark Connector**
