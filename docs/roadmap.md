
# FIWARE PySpark Connector Roadmap

This product is a FIWARE Generic Enabler. If you would like to learn about the overall
Roadmap of FIWARE, please check section "Roadmap" on the FIWARE Catalogue.

## Introduction

This section elaborates on proposed new features or tasks which are expected to be added to the product in the
foreseeable future. There should be no assumption of a commitment to deliver these features on specific dates or in the
order given. The development team will be doing their best to follow the proposed dates and priorities, but please bear
in mind that plans to work on a given feature or task may be revised. All information is provided as a general
guidelines only, and this section may be revised to provide newer information at any time.

## Short Term

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



## Medium Term

- [x] Make a working environment available with a docker image **Completed on 21/06/2023**
- [x] Subscribing tool **Completed on 20/09/2022**
- [x] Collapsed receiver and replier into one library and one configuration file **Completed on 20/09/2022**
- [x] Make the connector available as python package with pip **Completed on 21/06/2023**
- [ ] Efficiency improvements
- [x] Better Socket management (automatic ports) **Completed on 20/01/2023** 
- [ ] Find a **more elegant** way to keep only Spark sockets in memory without blocking the server
- [ ] Enhance subscription flexibility (see [Issue: Subscriptions Formats](#issue-subscription-formats))



## Long Term

- [ ] Evolving this "SISO" connector in a "MIMO" one to support multiple spark jobs (see [Issue: SISO](#issue-siso))
- [ ] Include support for NGSI-LD temporal API
- [ ] Include support for brokering systems such as Kafka or ActiveMQ
- [ ] Adding security to connections (see [Issue: Security](#issue-security))
- [ ] Adding conditions in the subscription tool
- [ ] Extensive tests on full production environments
- [ ] Bug Fixing (see [Bug fixes](#bug-fixes))


### Issue: SISO
It is important to underline that currently this connector support a single-input single-output connection, limiting to **1** the number of supported spark job per connector. To implement multiple connectors, it is necessary to run another spark job with different addresses. 

### Issue: Security
Currently it is strongly reccomended to use this connector in local. We are currently working on integrating other FIWARE solutions, as Keyrock and Wilma to integrate resource control.


### Issue: Subscription Formats
Currently, receiver supports only subscriptions with **Normalized Format**.


### Bug Fixes

- [x] If the Orion Broker is continuously streaming while the connector is configuring, the multi-thread socket will save the HTTP Server socket as Apache Client, blocking the execution of the whole program. **Fixed on 14/04/22**
- [x] If some special character is sent from the Orion Broker (i.e Ü or ß) to the receiver, the utf-8 conversion will send it with the escape character *\\* which is not allowed by the JSON Decoder. This will rise an exception. **Fixed On 20/01/2023**

