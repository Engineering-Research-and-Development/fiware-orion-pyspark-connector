### RECEIVER-SIDE-CONFIGURATION ###

HTTPADDRESS = "10.0.2.15"
HTTPPORT = 8061
SOCKETADDRESS = 'localhost'
SOCKETPORT = 9998
REQUEST_COMPLETENESS = True
SOCKET_BUFFER = 2048
MAX_CONCURRENT_CONNECTIONS = 20




### REPLIER-SIDE-CONFIGURATION ###

API_URL = "http://localhost:1026/v2/entities/urn:ngsi-ld:Product:010/attrs/price/"
METHOD = "PUT" #Choose among POST, PUT or PATCH
FIWARE_SERVICE = "opcua_car"
FIWARE_SERVICEPATH = "/demo"
CONTENT_TYPE = "application/json; charset=utf-8"
BLUEPRINTFILE = "Test.txt"
PLACEHOLDER = "%%TOREPLACE%%"





### Connector Base Classes




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
