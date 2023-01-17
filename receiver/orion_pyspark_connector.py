#!/usr/bin/env python
# coding: utf-8

import json
import requests
import socket
import time

from http.server import BaseHTTPRequestHandler, HTTPServer
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.storagelevel import StorageLevel
from typing import Union, Tuple, List, Type, Any
from threading import Thread
from datetime import datetime

import connectorconf
from connectorconf import NGSIAttribute, NGSIEntityv2, NGSIEntityLD, NGSIEventv2, NGSIEventLD



### RECEIVER-SIDE FUNCTIONS ###

def parse_context(api_json: dict) -> Tuple[str, bool]:
    '''
    This function checks if payload is "NGSI-LD" and returns its context,
    otherwise returns False.
    Context is checkable in both "Link" Header, otherwise in JSON body
    '''
    context = json.get("Link", "")
    if context:
        return context, True
    else:
        context = json.get("Body", {}).get("@context", "")
        if context:
            return context, True
        else:
            return "", False

        
def parse_entities(api_json: dict) -> List[Union[NGSIEntityv2, NGSIEntityLD]]:
    '''
    A function to parse Entity in format of NGSI v2 or LD
    based on the JSON body
    '''

    #Checking all entities in JSON
    entities_data = json.get("Body", {}).get("data", [])
    entities = []
    for ent in entities_data:
        ent_id = ent.get("id")
        ent_type = ent.get("type")
        attributes = {}

        # Checking for all attributes in entity except for id and type
        for key in ent.keys():
            if key not in ["id", "type"]:
                if ent[key]['type'] == "Relationship":
                    attribute = NGSIAttribute(ent[key]['type'], ent[key]['object'],
                                              ent[key].get("metadata", {}))
                else:
                    attribute = NGSIAttribute(ent[key]['type'], ent[key]['value'],
                                              ent[key].get("metadata", {}))
                attributes[key] = attribute

        # Checking for Linked Data Flag
        context, is_ld = parse_context(json)
        if is_ld:
            entity = NGSIEntityLD(ent_id, ent_type, attributes, context)
        else:
            entity = NGSIEntityv2(ent_id, ent_type, attributes)
        entities.append(entity)
    return entities


    
def parse(structured_NGSI_request : str) -> Union[NGSIEventv2, NGSIEventLD]:
    '''
    A function to convert API response into NGSIEvents
    '''
    
    api_json = json.loads(structured_NGSI_request)
    timestamp = api_json.get("timestamp", "")
    service = api_json.get("Fiware-Service", "")
    service_path = api_json.get('Fiware-Servicepath', "")
    entities = parse_entities(json)
    _, is_ld = parse_context(json)

            
    if is_ld:
        return NGSIEventLD(timestamp, service, service_path, entities)
    else:
        return NGSIEventv2(timestamp, service, service_path, entities)



class ServerThread(Thread):
    
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server
        self.awaken = False
        
    def awake(self):
        '''
        Set the 'awaken' variable to True, starting the server
        '''
        self.awaken = True
        
        
    def run(self):
        '''
        Wait until 'awaken' is True, then start the HTTP Server
        '''
        try:
            while not self.awaken:
                pass
            print('Starting HTTP Server...')
            self.server.serve_forever()
        except KeyboardInterrupt: 
            print('Server Stopped')
            


class ConnectionThread(Thread):
    '''
    Class to manage connections between sockets.
    '''
    def __init__(self, server_socket, client_socket, client_address, first_client):
        Thread.__init__(self)
        self.server_socket = server_socket
        self.client_socket = client_socket
        self.client_address = client_address
        self.first_client = first_client
        
    
    def run(self):
        '''
        Enstablish and manage independent connections from the current client with
        the pySpark client ('first_client'). 
        '''
        print("Connection Open from: {}".format(self.client_address))


        # Case 1: receiving data from pySpark socket and sinking them.
        if self.client_socket == self.first_client:
            try:
                while True:
                    data = self.client_socket.recv(connectorconf.SOCKET_BUFFER)
            except KeyboardInterrupt:
                print('Closed Connection')
                self.stop()   
        # Case 2: receive data from other clients.
        else:    
            try:
                while True:
                    data = self.client_socket.recv(connectorconf.SOCKET_BUFFER)
                    if data:
                        # Sending received data to pySpark
                        self.first_client.sendall(data)
                    else:
                        print("Received all from: {}".format(self.client_address))
                        if self.first_client != self.client_socket:
                            self.client_socket.close()
                            raise KeyboardInterrupt            
            except KeyboardInterrupt:
                print("Closed Connection from: {}".format(self.client_address))


class SocketThread(Thread):
    '''
    This class implements the MultiThread Socket Server, opening a server that receives messages
    from multiple threads. This server keeps trace of the instance of the HTTP Endpoint
    to awaken it when pySpark connects. This choice was made to overcome the problem of knowing
    the 'input-side' socket address of pySpark.
    '''
    
    def __init__(self, server_socket, server_address, server_thread):
        Thread.__init__(self)
        self.server_socket = server_socket
        self.server_address = server_address
        #TODO: Fix apache client socket saving.
        self.server_thread = server_thread
        self.first_client = None
        
        
    def run(self):
        '''
        Function that runs the thread, allowing the first client to connect to be set
        as 'first_client' which receives data from other sockets, awakening the HTTP server.
        By doing so, we ensure that the first connection is ensured by pySpark withing the program execution.
        This method should be improved, if possible., by searching how to recognize pySpark socket.
        '''

        try:
            self.server_socket.listen(connectorconf.MAX_CONCURRENT_CONNECTIONS)
            print('server socket opened')
            while True:    
                (client, client_address) = self.server_socket.accept()
                if self.first_client == None:
                    self.first_client = client
                    print("Awakening Server")
                    self.server_thread.awake()
                else:
                    connection_thread  = ConnectionThread(self.server_socket, client, client_address, self.first_client)
                    connection_thread.start()
        except KeyboardInterrupt:
            self.server_socket.close()
            print('socket closed')
        finally:
            self.server_socket.close()
            print('socket closed')


def structureNGSIRequest(request: str, body: str, timestamp: str) -> str:
    '''
    This function checks from the configuration file if the incoming message should be interpreted
    as a regular Context Broker Subscription (containing both headers and body) or if the message
    is sent via CURLS (body only).
    Based on the result, it starts to build the correct message, decoding it from the HTTP Response.
    '''
    # Case 1: Completeness (Headers + Body)
    if connectorconf.REQUEST_COMPLETENESS:
        message = "{"
        
        for line in body.split(","):
            if "notifiedAt" in line:
                timestamp_line = line
                iso_timestamp = timestamp_line.split('"')[3]
            else:
                iso_timestamp = timestamp.isoformat()   
        message = message + '"{}":"{}",'.format("timestamp", iso_timestamp)
        
        for field in request.headers:
            message = message + '"{}":"{}",'.format(field,request.headers[field].replace('"', "'"))
    

        # Cutting away binary character refuses from body
        message = message + '"Body":{}'.format(body[2:-1])
        message = message + "}\n"
        

    # Case 2: Uncompleteness (Raw Body only)
    else: 
        message = '{}\n'.format(body[2:-1])
    
    return message


class OrionPysparkRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        message = "Hello world!"
        self.wfile.write(bytes(message, "utf8"))
        return
    
    def run():
        print('Running Server...')

       
    def do_POST(self):
        '''
        Overridden POST function:
        - The server receives data from Orion or from CURL requests.
        - It structures and NGSI Request to be parsed
        - Set up a connection with the MultiThread Socket Server and sends received data
        - If succeeds, sends a confirmation message
        '''
        timestamp = datetime.now()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
      
        msg=structureNGSIRequest(self, str(post_data), timestamp)  
	    
        socket_to_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_to_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #TODO: Currently it is impossible to bind a fixed address since broker sends data too fast
        socket_to_send.connect((connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT))
        socket_to_send.send(msg.encode("utf-8"))
        socket_to_send.close()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode("utf-8"))
        
        
        
def StartConnector():
    '''
    Function that starts the connector, hence setting up both the Multi-Thread Socket server
    and the HTTP Endpoint in "sleeping mode". It will be awakened after the first pySpark connection.
    '''

    socket_address = (connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    s.bind(socket_address)

    server_address = (connectorconf.HTTPADDRESS, connectorconf.HTTPPORT)
    print(server_address)
    httpd = HTTPServer(server_address, OrionPysparkRequestHandler)

    threadserver = ServerThread(httpd)
    threadserver.start()

    threadsocket = SocketThread(s, socket_address, threadserver)
    threadsocket.start()




def Prime(sparkcontext: Type[SparkContext], sliding_window_seconds: float, storage : Type[StorageLevel]) -> Tuple[ Union[Type[NGSIEventv2], Type[NGSIEventLD]], Type[StreamingContext]] :

    StartConnector()
    ssc = StreamingContext(sparkcontext, sliding_window_seconds)
    record = ssc.socketTextStream(connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT, storageLevel=storage)


    NGSI_event = record.map(lambda x: parse(x))
    return NGSI_event, ssc
	

	
	

### REPLIER-SIDE FUNCTIONS ###


def listify(values: Any) -> List[Any]:
    
    if type(values) != list:
        values = [values]
            
    return values

        
def replaceJSON(values: Any) -> str:
    '''
    Function to replace values inside the 'BLUEPRINTFILE' where the 
    'PLACEHOLDER string is encountered, using the same encountering order.
    '''
    values = listify(values)

    with open(connectorconf.BLUEPRINTFILE, "r") as blueprint_file:
        blueprint_content=blueprint_file.read()
        blueprint_content = blueprint_content.replace("\n", " ")

        for v in values:
            blueprint_content = blueprint_content.replace(connectorconf.PLACEHOLDER, str(v), 1)
        
    return blueprint_content


def sendRequest(message: str, api_url: str, api_method: str) -> str:
    '''
    Function to send data to the context broker based on the 'api_method'
    '''

    headers= {"Content-Type": connectorconf.CONTENT_TYPE, 
              "Fiware-Service" : connectorconf.FIWARE_SERVICE,
              "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}

    try:
        if api_method == "POST":
            reply = requests.post(api_url, message, headers=headers)
        elif api_method == "PUT":
            reply = requests.put(api_url, message, headers=headers)
        elif api_method == "PATCH":
            reply = requests.patch(api_url, message, headers=headers)
        else:
            raise ValueError("Method not allowed")
        return reply.text
    except Exception as e:
        return e
                
        
def ReplyToBroker(values: Any, api_url=connectorconf.API_URL: str, api_method=connectorconf.METHOD: str) -> str:
    '''
    Function for structured and complex requests, using the 'BLUEPRINTFILE' specified in the
    configuration file and replacing values using the 'PLACEHOLDER' string.
    Values MUST be in the same order of the replacing strings.
    Builds the request on-the-fly and send it to the context broker
    '''
    message = replaceJSON(values)
    return sendRequest(message, api_url, api_method)
    
    
def SemistructuredReplyToBroker(values: Any, body: str, api_url=connectorconf.API_URL: str, api_method=connectorconf.METHOD: str) -> str:
    '''
    Function for averagely complex requests, passing an encoded request body and some values
    that have to be replaced in body when the 'PLACEHOLDER' string is encountered.
    Values MUST be in the same order of the replacing strings.
    Builds the request on-the-fly and send it to the context broker.
    '''
    values = listify(values)
    for v in values:
        body = body.replace(connectorconf.PLACEHOLDER, str(v), 1)
        
    return sendRequest(body, api_url, api_method)
   
    
def UnstructuredReplyToBroker(body: str, api_url=connectorconf.API_URL: str, api_method=connectorconf.METHOD: str) -> str:
    '''
    Function for simple and short requests, passing directly the request body.
    No correctness is ensured by the connector, so every character has to be checked by the user.
    Sends the passed message to the context broker.
    '''
    return sendRequest(body, api_url, api_method)

    




    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
	


