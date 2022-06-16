# FIWARE Orion PySpark Connector 
[![](https://nexus.lab.fiware.org/static/badges/chapters/core.svg)](https://www.fiware.org/developers/catalogue/)
[![License: AGPL](https://img.shields.io/github/license/Engineering-Research-and-Development/iotagent-opcua.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Support badge](https://img.shields.io/badge/support-stackoverflow-orange)](https://stackoverflow.com/questions/tagged/fiware+orion+pyspark+connector)
[![Documentation badge](https://readthedocs.org/projects/fiware-orion-pyspark-connector/badge/?version=latest)](https://fiware-orion-pyspark-connector.readthedocs.io)
![Status](https://nexus.lab.fiware.org/repository/raw/public/badges/statuses/incubating.svg)
<br/>
[![Coverage Status](https://coveralls.io/repos/github/Engineering-Research-and-Development/fiware-orion-pyspark-connector/badge.svg?branch=main)](https://coveralls.io/github/Engineering-Research-and-Development/fiware-orion-pyspark-connector?branch=main)


The FIWARE Orion PySpark Connector is a FIWARE Generic Enabler (GE) creating a data bridge between the FIWARE Orion Context Broker and PySpark

| :books: [Documentation](https://fiware-orion-pyspark-connector.readthedocs.io/en/latest/) | :whale: [Docker Hub](https://hub.docker.com/r/rdlabengpa/fiware-orion-pyspark-connector) | :dart: [Roadmap](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/main/docs/roadmap.md) |
| -------------------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |

## Table of Contents

-   [What Is Orion PySpark Connector](#what-is-orion-pyspark-connector)
-   [Why Use Orion PySpark Connector](#why-use-orion-pyspark-connector)
-   [Requirements and installation](docs/requirements.md)
-   [Quick start](docs/quick_start.md)
-   [Docker](docs/docker.md)
-   [Roadmap](docs/roadmap.md)


## What Is Orion PySpark Connector
Orion PySpark Connector is a FIWARE Generic Enabler (GE) made of a receiver and a replier subcomponents allowing a bidirectional communication between the FIWARE Orion Context Broker (CB) and PySpark. The component works on a low-level socket communication implementing a message passing interface between the two aforementioned counterparts. This interface is equipped with a parser function, hence permitting the creation of both NGSIv2 and NGSI-LD entities ready to use in a custom PySpark algorithm. Once data are preprocessed inside the PySpark evnironment, the component also provide a write-back interface (via REST API) to the Orion CB.


## Why Use Orion PySpark Connector
Orion PySpark Connector was created with the idea of expanding the FIWARE Orion CB's environment to merge with python's one. Python is currently one of the most used programming languages for data analysis, providing lots of scientific libraries for data processing and visualization. Orion, on the other hand, is a powerful tool allowing the management of context elements and sending updates via subscriptions. This connector is able to open a communication path between these two instruments and to combine the advantages they provide at a little-to-none cost.


## Component Architecture
![Pysparkconnector drawio](https://user-images.githubusercontent.com/103200695/171157871-a3904c76-e961-45d5-ad01-507604944ad2.png)


### Receiver Side

The Orion-PySpark receiver is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a PySpark job.
The tool is represented in the following diagram and it is made of:


-   **`Connector Library`**: Set of functions and class definition for NGSI Events
-   **`Connector configuration file`**: Configuration file to configure the connector servers and mode.


### Replier Side

The Orion-PySpark replier is currently a library composed by:
- **`Replier Lib`**: Python 3.8 library to import and use in a custom spark job that converts a stream of processed data into a Http request body and sends it with a API request.
- **`Replier configuration file`**: a configuration file to set the API URL, method, some fundamental HTTP headers and the placeholder character for the request body blueprint

## License

The FIWARE Orion PySpark Connector is licensed under [Affero General Public License (GPL) version 3](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/main/LICENSE.txt).

© 2022 Engineering Ingegneria Informatica S.p.A.


### Are there any legal issues with AGPL 3.0? Is it safe for me to use?

No problem in using a product licensed under AGPL 3.0. Issues with GPL (or AGPL) licenses are mostly related with the
fact that different people assign different interpretations on the meaning of the term “derivate work” used in these
licenses. Due to this, some people believe that there is a risk in just _using_ software under GPL or AGPL licenses
(even without _modifying_ it).

For the avoidance of doubt, the owners of this software licensed under an AGPL 3.0 license wish to make a clarifying
public statement as follows:

"Please note that software derived as a result of modifying the source code of this software in order to fix a bug or
incorporate enhancements is considered a derivative work of the product. Software that merely uses or aggregates (i.e.
links to) an otherwise unmodified version of existing software is not considered a derivative work, and therefore it
does not need to be released as under the same license, or even released as open source."
