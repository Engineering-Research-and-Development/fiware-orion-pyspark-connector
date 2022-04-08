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

<div style="text-align:center">
  ![Connector-diagram](https://user-images.githubusercontent.com/103200695/162405802-3bc222df-63aa-41d9-a347-3c270d8ab8a4.png)
</div>

                                     



-   **`Connector Library & NGSI classes`**: Set of functions and class definition for NGSI Events
-   **`Connector start`**: Python 3.8 code to start the connector.
-   **`* Primers`**: Python 3.8 code to implement in a pyspark job to obtain .

# Installation


