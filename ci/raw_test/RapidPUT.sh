#!/bin/bash

for i in {0..100..1}
do
   echo $i
   curl -X PUT http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/value -H "Content-Type: text/plain" -d "$i"
done


