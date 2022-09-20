
## Roadmap

### Short Term

- [x] Use tests for Receiver. **Completed on 12/04/22**
- [x] Adding a Replier to write back to the broker. **Completed on 13/04/22**
- [x] Adding NGSI-LD support to Receiver **Completed on 13/04/22**
- [x] Use test for Replier **Completed on 14/04/22**
- [x] Find an elegant way to keep Spark socket in memory **Completed on 14/04/22**
- [x] Improve usability for the Receiver **Completed on 15/04/22**
- [x] Adding NGSI-LD support to Replier **Completed on 19/04/22**
- [x] ~~Write a definitive JSON structurer tool~~ **Objective changed on 19/04/22**
- [x] Made a flexible request body constructor **Completed on 19/04/22**
- [x] Tests for NGSI-LD Support for both receiver and replier side. **Completed on 26/07/2022**
- [x] Test for performances **Completed on 26/07/2022**


### Medium Term

- [ ] Make the connector available with a docker image **Working**
- [x] Subscribing tool **Completed on 20/09/2022**
- [x] Collapsed receiver and replier into one library and one configuration file **Completed on 20/09/2022**
- [ ] Efficiency improvements
- [ ] Better Socket management (automatic ports)
- [ ] Find a **more elegant** way to keep only Spark sockets in memory without blocking the server



### Long Term

- [ ] Evolving this "SISO" connector in a "MIMO" one to support multiple spark jobs
- [ ] Adding security to connections
- [ ] Adding conditions in the subscription tool



## Current Version Limits

It is important to underline that currently this connector support a single-input single-output connection, limiting to **1** the number of supported spark job per connector. To implement multiple connectors, it is necessary to run another spark job with different addresses.  <br />
It is strongly reccomended to use this connector in local: a future version implementing security will be provided <br />
Currently, receiver supports only subscriptions with **Normalized Format**

### Known Issues

- [x] If the Orion Broker is continuously streaming while the connector is configuring, the multi-thread socket will save the HTTP Server socket as Apache Client, blocking the execution of the whole program. **Fixed on 14/04/22**
- [ ] If some special character is sent from the Orion Broker (i.e Ü or ß) to the receiver, the utf-8 conversion will send it with the escape character *\\* which is not allowed by the JSON Decoder. This will rise an exception. **Working On**

