#!/bin/bash

sleep 90
curl -vX PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "10"
