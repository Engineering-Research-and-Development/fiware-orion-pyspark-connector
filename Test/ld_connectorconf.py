import socket


### RECEIVER-SIDE-CONFIGURATION ###

class ReceiverConfiguration():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Address and port of the HTTP Endpoint
        self.http_address = socket.gethostbyname(socket.gethostname())
        self.http_port = 8061
        # Address and port of the Multi-Thread Socket Server ans PySpark output
        self.socket_address = 'localhost'
        self.socket_port = 9998
        # Set up the connector to receive HTTP data (True) or strings (False)
        self.request_completeness = True
        # Socket buffer size
        self.socket_buffer = 2048
        # Multi-Thread socket server allowed concurrenct connections.
        self.max_concurrent_connections = 20



### REPLIER-SIDE-CONFIGURATION ###

class ReplierConfiguration():
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Context Broker API to send back data
        self.api_url = "http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Product:010/attrs/price/"
        self.api_method = "PUT" #Choose among POST, PUT or PATCH
        # Context broker service and subservice
        self.fiware_service = ""
        self.fiware_servicepath = "/"
        # Content Type of the request
        self.content_type = "application/ld+json; charset=utf-8"
        # Advanced configuration for more complex requests 
        self.blueprint_file = "Test.txt"
        self.placeholder_string = "%%TOREPLACE%%"


RECV_SINGLETON = ReceiverConfiguration()
REPL_SINGLETON = ReplierConfiguration()


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
