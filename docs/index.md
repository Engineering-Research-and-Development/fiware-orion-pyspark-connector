# FIWARE Orion PySpark Connector 

[![License: AGPL](https://img.shields.io/github/license/Engineering-Research-and-Development/iotagent-opcua.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Support badge](https://img.shields.io/badge/support-stackoverflow-orange)](https://stackoverflow.com/questions/tagged/fiware+iot)
[![Documentation badge](https://readthedocs.org/projects/fiware-orion-pyspark-connector/badge/?version=latest)](https://fiware-orion-pyspark-connector.readthedocs.io)
<br/>

The FIWARE Orion PySpark Connector is a FIWARE Generic Enabler (GE) creating a data bridge between the FIWARE Orion Context Broker and PySpark

## What Is Orion PySpark Connector
Orion PySpark Connector is a FIWARE Generic Enabler (GE) made of a receiver and a replier subcomponents allowing a bidirectional communication between the FIWARE Orion Context Broker (CB) and PySpark. The component works on a low-level socket communication implementing a message passing interface between the two aforementioned counterparts. This interface is equipped with a parser function, hence permitting the creation of both NGSIv2 and NGSI-LD entities ready to use in a custom PySpark algorithm. Once data are preprocessed inside the PySpark evnironment, the component also provide a write-back interface (via REST API) to the Orion CB.

## Why Use Orion PySpark Connector
Orion PySpark Connector was created with the idea of expanding the FIWARE Orion CB's environment to merge with python's one. Python is currently one of the most used programming languages for data analysis, providing lots of scientific libraries for data processing and visualization. Orion, on the other hand, is a powerful tool allowing the management of context elements and sending updates via subscriptions. This connector is able to open a communication path between these two instruments and to combine the advantages they provide at a little-to-none cost.
