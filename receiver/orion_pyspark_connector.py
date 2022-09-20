#!/usr/bin/env python
# coding: utf-8

import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.storagelevel import StorageLevel

from threading import Thread
import socket
import time
from datetime import datetime
import requests

import connectorconf
from connectorconf import NGSIAttribute, NGSIEntityv2, NGSIEntityLD, NGSIEventv2, NGSIEventLD



### RECEIVER-SIDE FUNCTIONS ###
        


def ParseToJSON(API):
    
    j = json.loads(API)
    #print(j)
    return j

    
def Parse(API):
    
    isLD = False
    
    
    json = ParseToJSON(API)
    
    
    try:
        timestamp = json['timestamp']
    except:
        return json
        
    
    try :
        service = json['Fiware-Service']
    except:
        service = ""
        
    try:
        servicepath= json['Fiware-Servicepath']
    except:
        servicepath = ""
        
    try:
    	context = json['Link']
    	isLD = True
    except:
        try:
            context = json['Body']['@context']
            isLD = True
        except:
            context = ""
            
    
    body = json['Body']
    entities = body['data']


    entitylist = []
    for ent in entities:
        keys = list(ent)
        attrs = {}
        
        ID = ent['id']
        keys.remove('id')
        typ = ent['type']
        keys.remove('type')
        
        for i in range (0, len(keys)):
            att = ent[keys[i]]
            atttype = att['type']
            
            if atttype == "Relationship":
                attval = att['object']
            else:
                attval = att['value']
            
            
            try:
            	attmeta = att['metadata']
            except:
            	attmeta = {}
            attribute = NGSIAttribute(atttype, attval, attmeta)
            attrs[keys[i]] = attribute
       
        if isLD:
            entity = NGSIEntityLD(ID, typ, attrs, context)
        else:
            entity = NGSIEntityv2(ID, typ, attrs)
        
        entitylist.append(entity)
            
    if isLD:
        event = NGSIEventLD(timestamp, service, servicepath, entitylist)
    else:
        event = NGSIEventv2(timestamp, service, servicepath, entitylist)
    
    
    return event




class ServerThread(Thread):
    
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server
        self.awaken = False
        
    def Awake(self):
        self.awaken = True
        
        
    def run(self):
        try:
            print(not self.awaken)
            while not self.awaken:
                pass
            print('Starting HTTP Server...')
            self.server.serve_forever()
        except KeyboardInterrupt: 
            print('Server Stopped')
            


class ConnectionThread(Thread):
    
    def __init__(self, serv, cli, cliaddress, firstcli):
        Thread.__init__(self)
        self.sock = serv
        self.cli = cli
        self.cliaddress = cliaddress

        self.firstcli = firstcli
        

    
    
    def run(self):
        
        print("Connection Open from: {}".format(self.cliaddress))
        if self.cli == self.firstcli:
            
            try:
                while True:
                    data = self.cli.recv(connectorconf.SOCKET_BUFFER)

            
            except KeyboardInterrupt:
                print('Closed Connection')
                self.stop()
                
        else:    
            try:
                while True:
                    data = self.cli.recv(connectorconf.SOCKET_BUFFER)
                    if data:
                        self.firstcli.sendall(data)
                    else:
                        print("Received all from: {}".format(self.cliaddress))
                        if self.firstcli != self.cli:
                            self.cli.close()
                            raise KeyboardInterrupt

                        
            except KeyboardInterrupt:
                print("Closed Connection from: {}".format(self.cliaddress))
        


class SocketThread(Thread):
    
    
    def __init__(self, sock, address, serverthread):
        Thread.__init__(self)
        self.sock = sock
        self.address = address
        #TODO: Fix apache client socket saving.
        self.serverthread = serverthread
        self.firstcli = None
        
           
        
        
    def run(self):
        try:
            self.sock.listen(connectorconf.MAX_CONCURRENT_CONNECTIONS)
            print('server socket opened')

            while True:    
                (cli, cliadd) = self.sock.accept();
                if self.firstcli == None:
                    self.firstcli = cli
                    print("Awakening Server")
                    self.serverthread.Awake()
                else:
                    tr = ConnectionThread(self.sock, cli, cliadd, self.firstcli)
                    tr.start()

        except KeyboardInterrupt:
            self.sock.close()
            print('socket closed')
        finally:
            self.sock.close()
            print('socket closed')


  
    
    
def StructureNGSIRequest(request, body, timestamp):


    if connectorconf.REQUEST_COMPLETENESS: #HEADERS + BODY
    
        message = "{"
        
        for line in body.split(","):
            if "notifiedAt" in line:
                tsline = line
                ts = tsline.split('"')[3]
            else:
                ts = timestamp.isoformat()

            
    
        message = message + '"{}":"{}",'.format("timestamp", ts)
        
    
        for field in request.headers:
            message = message + '"{}":"{}",'.format(field,request.headers[field].replace('"', "'"))
    
        message = message + '"Body":{}'.format(body[2:-1])
        message = message + "}\n"
        
        
        
    else: #BODY ONLY
        message = '{}\n'.format(body[2:-1])
        #print(message)
        
    
    return message
 




class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        message = "Hello world!"
        self.wfile.write(bytes(message, "utf8"))
        return
    
    def run(ssc):
        print('Running Server...')

        
       
    def do_POST(self):
        ts = datetime.now()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
      
        msg=StructureNGSIRequest(self, str(post_data), ts)
        
	    
	    
        socket_to_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_to_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #TODO: Currently it is impossible to bind a fixed address since broker sends data too fast
        #socket_to_send.bind((connectorconf.HTTPSOCKETADDRESS, connectorconf.HTTPSOCKETPORT))
        socket_to_send.connect((connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT))
        socket_to_send.send(msg.encode("utf-8"))

        socket_to_send.close()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        self.wfile.write("<html><body><h1>POST!</h1></body></html>".encode("utf-8"))
        
        
        
def StartConnector():

    socket_address = (connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    s.bind(socket_address)



    server_address = (connectorconf.HTTPADDRESS, connectorconf.HTTPPORT)
    print(server_address)


    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)



    threadserver = ServerThread(httpd)
    threadserver.start()

    threadsocket = SocketThread(s, socket_address, threadserver)
    threadsocket.start()





def Prime(sparkcontext, sliding_window_seconds, storage):

    StartConnector()
    ssc = StreamingContext(sparkcontext, sliding_window_seconds)
    record = ssc.socketTextStream(connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT, storageLevel=storage)


    NGSI_event = record.map(lambda x: Parse(x))
    return NGSI_event, ssc
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

### REPLIER-SIDE FUNCTIONS ###


def Listify(values):
    
    if type(values) != list:
        values = [values]
            
    return values

        
        
def ReplaceJSON(values):
    
    values = Listify(values)
    f = open(connectorconf.BLUEPRINTFILE, "r")
    text=f.read()
    f.close()
    text = text.replace("\n", " ")
    for v in values:
        text = text.replace(connectorconf.PLACEHOLDER, str(v), 1)
        
    return text
        
        
def ReplyToBroker(values, apiURL=connectorconf.API_URL, apiMethod=connectorconf.METHOD):
    
    headers= {"Content-Type": connectorconf.CONTENT_TYPE, "Fiware-Service" : connectorconf.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}
    msg = ReplaceJSON(values)
    
    try:
        if apiMethod == "POST":
            reply = requests.post(apiURL, msg, headers=headers)
        elif apiMethod == "PUT":
            reply = requests.put(apiURL, msg, headers=headers)
        elif apiMethod == "PATCH":
            reply = requests.patch(apiURL, msg, headers=headers)
        else:
            print("Method not allowed")
        reply = reply.text
    except Exception as e:
        reply = e
        
    return reply
    
    

def SemistructuredReplyToBroker(values, body, apiURL=connectorconf.API_URL, apiMethod=connectorconf.METHOD):
    
    headers= {"Content-Type": connectorconf.CONTENT_TYPE, "Fiware-Service" : connectorconf.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}

    values = Listify(values)
    for v in values:
        body = body.replace(connectorconf.PLACEHOLDER, str(v), 1)
    
    
    try:
        if apiMethod == "POST":
            reply = requests.post(apiURL, body, headers=headers)
        elif apiMethod == "PUT":
            reply = requests.put(apiURL, body, headers=headers)
        elif apiMethod == "PATCH":
            reply = requests.patch(apiURL, body, headers=headers)
        else:
            print("Method not allowed")
        reply = reply.text
    except Exception as e:
        reply = e
        
    return reply
   
    
def UnstructuredReplyToBroker(body, apiURL=connectorconf.API_URL, apiMethod=connectorconf.METHOD):
    
    
    headers= {"Content-Type": connectorconf.CONTENT_TYPE, "Fiware-Service" : connectorconf.FIWARE_SERVICE, "Fiware-Servicepath": connectorconf.FIWARE_SERVICEPATH}
    
    
    try:
        if apiMethod == "POST":
            reply = requests.post(apiURL, body, headers=headers)
        elif apiMethod == "PUT":
            reply = requests.put(apiURL, body, headers=headers)
        elif apiMethod == "PATCH":
            reply = requests.patch(apiURL, body, headers=headers)
        else:
            print("Method not allowed")
        reply = reply.text
    except Exception as e:
        reply = e
        
    return reply
    




    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
	


