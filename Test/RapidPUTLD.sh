sleep 30
curl -vX PATCH http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Building:store001/attrs/ -d @./Test/ld_payload.json -H "Content-Type: application/ld+json" -H "NGSILD-Tenant: orion"
sleep 5
curl -vX PATCH http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Building:store001/attrs/ -d @./Test/ld_payload.json -H "Content-Type: application/ld+json" -H "NGSILD-Tenant: orion"
sleep 5
curl -vX PATCH http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Building:store001/attrs/ -d @./Test/ld_payload.json -H "Content-Type: application/ld+json" -H "NGSILD-Tenant: orion"
