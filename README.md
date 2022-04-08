# fiware-orion-pyspark-connector


## Table of Contents

-   [What is this connector](#what-is-this-connector)
-   [Requirements and installation](#requirements-and-installation)
-   [Usage](#usage)
-   [Actual Version Limits](#actual-version-limits)
-   [Roadmap](#roadmap)
-   [License](#license)


## What is this connector

The orion-pyspark connector is currently a custom tool capable of receiving HTTP messages from a Orion broker and transform them to produce a batched stream of NGSI events to be processed by a pyspark job.
The tool is represented in the following diagram and it is made of:


![Connector-diagram](https://user-images.githubusercontent.com/103200695/162405802-3bc222df-63aa-41d9-a347-3c270d8ab8a4.png)


-   **`Connector Library & NGSI classes`**: Set of functions and class definition for NGSI Events
-   **`Connector start`**: Python 3.8 code to start the connector.
-   **`Primers (OPTIONAL)`**: Python 3.8 code to implement in a pyspark job to obtain a stream of NGSI Event objects



## Requirements and installation

The tool source code is written in Python 3.8 and this python version should be installed on the machine running the connector
On linux terminal:

```console
sudo apt update
sudo apt-get install python3.8
sudo apt-get install python3-pip
```

In the `requirements.txt` found in this repository file there is a serie of dependencies useful to load every library used in the connector.
Once downloaded this file, open the terminal in the repository folder and run the following commands:

```console
pip3 install -r requirements.txt
```

Now every required library to run the connector is ready. <br />
**N.B:** The requirements files contains requirement for the connector and the primer. Spark itself is omitted since it is assumed that this library is already installed. If spark is needed, use the following guide:

[Install Spark](https://towardsdatascience.com/installing-pyspark-with-java-8-on-ubuntu-18-04-6a9dea915b5b)


## Usage

Once installed the requirements, the connector is easy to use:
- Load files on the same machine running the spark job
- Modify the `conf.py` file in the repository to set up the IP address and port for both the HTTP Server and the multi-threading socket. **Don't use the same address and port for the HTPP Server and the Sockets**
- Make a subscription to the Orion Broker, inserting the HTTP server address and port
- Run the connector using 
```console
python3 connector_start.py
```

To obtain a stream of NGSI Events:

- **Optional** modify the `{}_Primer.py` file to set up the spark configuration
- **Optional** import the `{}_Primer.py` file (where {} indicates the name prefix of the file, i.e: NGSIV2) in your custom spark job and save both the event stream and the stream socket with the following code:

```python
import {}_primer as NGSI
event, ssc = NGSI.Prime()
#event variable contains the parsed stream, ssc is the stream itself. 
#Apply the pyspark algorithm on the event variable, then run the stream using ssc.run()
```

## Actual Version Limits

It is important to underline that currently this connector support a single-input single-output connection, limiting to **1** the number of supported spark job per connector. To implement multiple connectors, it is necessary to run another spark job with different addresses.  <\br>
It is strongly reccomended to use this connector in local: a future version implementing security will be provided


## Roadmap

### Short Term

- Efficiency improvements
- Better Socket management (automatic ports)
- Adding NGSI-LD support

### Medium Term

- Subscribing tool
- Evolving this "SISO" connector in a "MIMO" one to support multiple spark jobs

### Long Term
- Adding a Sink to write back to the broker.
- Adding security to connections


## License

This software is licensed under [GNU General Public License (GPL) version 3](./LICENSE.txt).


> Please note that software derived as a result of modifying the source code of this software in order to fix a bug or
> incorporate enhancements is considered a derivative work of the product. Software that merely uses or aggregates (i.e.
> links to) an otherwise unmodified version of existing software is not considered a derivative work, and therefore it
> does not need to be released as under the same license, or even released as open source.
