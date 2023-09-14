![py-spark](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/assets/103200695/2eec9346-b576-4f8d-84cb-ad57b49ce6f3)


The FIWARE PySpark Connector is a FIWARE Generic Enabler (GE) creating a data bridge between the FIWARE Context Brokers and PySpark.
<br/>
This project is part of [FIWARE](https://www.fiware.org/) For more information check the [FIWARE Catalogue](https://github.com/FIWARE/catalogue/tree/master/core)

 
## Table of Contents

- [What Is FIWARE PySpark Connector](#what-is-fiware-pyspark-connector)
- [Why Use FIWARE PySpark Connector](#why-use-fiware-pyspark-connector)
- [Quick start](docs/quick_start.md)
- [Requirements and installation](docs/requirements.md)
  - [Docker](docs/docker.md)
- [Step-by-Step Tutorial](docs/step_by_step.md)
- [Roadmap](docs/roadmap.md)


## What Is FIWARE PySpark Connector
FIWARE PySpark Connector is a FIWARE Generic Enabler (GE) made of a receiver and a replier subcomponents allowing a bidirectional communication between the FIWARE Context Brokers (CB) and PySpark. The component works on a low-level socket communication implementing a message passing interface between the two aforementioned counterparts. This interface is equipped with a parser function, hence permitting the creation of both NGSIv2 and NGSI-LD entities ready to use in a custom PySpark algorithm. Once data are preprocessed inside the PySpark evnironment, the component also provide a write-back interface (via REST API) to the CBs.


## Why Use FIWARE PySpark Connector
FIWARE PySpark Connector was created with the idea of expanding the FIWARE CB's environment to merge with python's one. Python is currently one of the most used programming languages for data analysis, providing lots of scientific libraries for data processing and visualization. Context brokers such as Orion, on the other hand, are powerful tools allowing the management of context elements and sending updates via subscriptions. This connector is able to open a communication path between these two instruments and to combine the advantages they provide at a little-to-none cost.


## Component Architecture
![Pysparkconnector drawio](https://user-images.githubusercontent.com/103200695/171157871-a3904c76-e961-45d5-ad01-507604944ad2.png)


The FIWARE-PySpark receiver is currently a custom tool capable of receiving HTTP messages from a context broker and transform them to produce a batched stream of NGSI events to be processed by a PySpark job.
The tool is represented in the above diagram and it is made of:


-   **`Connector Library`**: Set of functions to receive and reply to the context broker
-   **`Connector configuration file`**: Configuration file to configure the connector servers and mode, class definition for NGSI Events and Parameter configuration for replier side.
-   **`Subscribing Tool`**: Optional Library browsing the available entities in the context broker and allowing an easier subscription.


## License

The FIWARE PySpark Connector is licensed under [Affero General Public License (GPL) version 3](https://github.com/Engineering-Research-and-Development/fiware-orion-pyspark-connector/blob/main/LICENSE.txt).

© 2022 Engineering Ingegneria Informatica S.p.A.

PySpark Connector has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreements No  870062 [CAPRI](https://www.capri-project.com/).


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
