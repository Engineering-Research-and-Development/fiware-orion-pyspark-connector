### RECEIVER-SIDE-CONFIGURATION ###

# Address and port of the HTTP Endpoint
HTTPADDRESS = "10.0.2.15"
HTTPPORT = 8061
# Address and port of the Multi-Thread Socket Server ans PySpark output
SOCKETADDRESS = 'localhost'
SOCKETPORT = 9998
# Set up the connector to receive HTTP data (True) or strings (False)
REQUEST_COMPLETENESS = True
# Socket buffer size
SOCKET_BUFFER = 2048
# Multi-Thread socket server allowed concurrenct connections.
MAX_CONCURRENT_CONNECTIONS = 20


### REPLIER-SIDE-CONFIGURATION ###

# Context Broker API to send back data
API_URL = "http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/"
METHOD = "PUT" #Choose among POST, PUT or PATCH
# Context broker service and subservice
FIWARE_SERVICE = "opcua_car"
FIWARE_SERVICEPATH = "/demo"
# Content Type of the request
CONTENT_TYPE = "application/json; charset=utf-8"
# Advanced configuration for more complex requests 
BLUEPRINTFILE = "Test.txt"
PLACEHOLDER = "%%TOREPLACE%%"


### Connector Base Classes ###


class NGSIAttribute():
    
    def __init__(self, attrype, value, metadata):
        self.type = attrype
        self.value = value
        self.metadata = metadata
        

class NGSIEntityv2():
    
    def __init__(self, entityid, nodetype, attributes):
        self.id = entityid
        self.type = nodetype
        self.attrs = attributes



class NGSIEntityLD():
    
    def __init__(self, entityid, nodetype, attributes, context):
        self.context = context
        self.id = entityid
        self.type = nodetype
        self.attrs = attributes
        
        
class NGSIEventLD():
    
    def __init__(self, timestamp, svc, svcpath, entities):
        self.creationtime = timestamp
        self.service = svc
        self.servicePath = svcpath
        self.entities = entities
        

class NGSIEventv2():
    
    def __init__(self, timestamp, svc, svcpath, entities):
        self.creationtime = timestamp
        self.service = svc
        self.servicePath = svcpath
        self.entities = entities
