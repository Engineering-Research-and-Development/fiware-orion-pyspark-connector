#!/bin/bash

sleep 25
curl -vX PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "10"
sleep 5
curl -vX PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "10"
sleep 5
curl -vX PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "10"
sleep 5
curl -vX PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "10"
sleep 5
curl -vX PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "10"
