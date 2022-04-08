# fiware-orion-pyspark-connector


## Table of Contents

-   [What is this connector](#what-is-this-connector)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage: API Overview](#usage-api-overview)
-   [Maintainers](#maintainers)
-   [Roadmap](#roadmap)
-   [License](#license)


## What is this connector

The orion-pyspark connector is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a pyspark job.
The tool is represented in the following diagram and it is made of:

<p align="center">
  <img width="460" height="300" src="http://https://user-images.githubusercontent.com/103200695/162401586-22396bb7-6589-45f6-b7cc-0882af7d6c61.png">
</p>
                                     



-   **`Connector Library & NGSI classes`**: Set of functions and class definition for NGSI Events
-   **`Connector start`**: Python 3.8 code to start the connector.
-   **`* Primers`**: Python 3.8 code to implement in a pyspark job to obtain .

# Installation


