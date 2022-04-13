#!/usr/bin/env python
# coding: utf-8

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext, listener

from threading import Thread
import socket
import time
from datetime import datetime

import conf as connectorconf
import NGSIv2, NGSILD

from py4j.java_gateway import java_import, is_instance_of

from pyspark import RDD, SparkConf
from pyspark.serializers import NoOpSerializer, UTF8Deserializer, CloudPickleSerializer
from pyspark.context import SparkContext
from pyspark.storagelevel import StorageLevel
from pyspark.streaming.dstream import DStream
from pyspark.streaming.util import TransformFunction, TransformFunctionSerializer



def ParseToJSON(API):
    
    j = json.loads(API)
    #print(j)
    return j

    

def ParseToNGSIv2(API):
    
    json = ParseToJSON(API)
    timestamp = json['timestamp']
    service = json['User-Agent']
    servicepath= json['Fiware-Servicepath']
    
    body = json['Body']
    entities = body['data']


    entitylist = []
    
    for ent in entities:
        keys = list(ent)
        attrs = {}
        
        ID = ent['id']
        typ = ent ['type']
        
        for i in range (2, len(keys)):
            att = ent[keys[i]]
            atttype = att['type']
            attval = att['value']
            attmeta = att['metadata']
            attribute = NGSIv2.Attributev2(atttype, attval, attmeta)
            attrs[keys[i]] = attribute
       
        entity = NGSIv2.Entityv2(ID, typ, attrs)
        entitylist.append(entity)
            
    
    event = NGSIv2.NGSIEventv2(timestamp, service, servicepath, entitylist)
    
    return event
    
    
def ParseToNGSILD(API):
    
    json = ParseToJSON(API)
    timestamp = json['timestamp']
    service = json['Fiware-Service']
    servicepath= json['Fiware-Servicepath']
    context = json['Link']
    body = json['Body']
    entities = body['data']


    entitylist = []
    
    for ent in entities:
        keys = list(ent)
        attrs = {}
        
        ID = ent['id']
        typ = ent ['type']
        
        for i in range (2, len(keys)):
            att = ent[keys[i]]
            atttype = att['type']
            attval = att['value']
            try:
            	attmeta = att['metadata']
            except:
            	attmeta = {}
            attribute = NGSILD.AttributeLD(atttype, attval, attmeta)
            attrs[keys[i]] = attribute
       
        entity = NGSILD.EntityLD(ID, typ, attrs, context)
        entitylist.append(entity)
            
    
    event = NGSILD.NGSIEventLD(timestamp, service, servicepath, entitylist)
    
    return event


class ServerThread(Thread):
    
    
    def __init__(self, server):
        Thread.__init__(self)
        self.server = server
        
        
    def run(self):
        try:
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
    
    
    def __init__(self, sock, address):
        Thread.__init__(self)
        self.sock = sock
        self.address = address
        #TODO: Fix apache client socket saving.
        self.firstcli = None
        
        
    def run(self):
        try:
            self.sock.listen(10)
            print('server socket opened')

            while True:    
                (cli, cliadd) = self.sock.accept();
                if self.firstcli == None:
                    
                    if cliadd[1] != connectorconf.HTTPSOCKETPORT:
                    	self.firstcli = cli
                    	print("Saving streaming connector address")
                else:
                    tr = ConnectionThread(self.sock, cli, cliadd, self.firstcli)
                    tr.start()

        except KeyboardInterrupt:
            self.sock.close()
            print('socket closed')
        finally:
            self.sock.close()
            print('socket closed')



def StructureNGSIv2Request(request, body, timestamp):
    
    
    
    if connectorconf.REQUEST_COMPLETENESS: #HEADERS + BODY
    
        message = "{"
        ts = timestamp.isoformat()
    
        message = message + '"{}":"{}",'.format("timestamp", ts)
    
        for field in request.headers:
            message = message + '"{}":"{}",'.format(field,request.headers[field])
    
        message = message + '"Body":{}'.format(body[2:-1])
        message = message + "}\n"
        
    else: #BODY ONLY
        message = '{}\n'.format(body[2:-1])
    
    return message
    
    
    
    
def StructureNGSILDRequest(request, body):


    if connectorconf.REQUEST_COMPLETENESS: #HEADERS + BODY
    
        message = "{"
        
        for line in body.split(","):
            if "notifiedAt" in line:
                tsline = line
        
        ts = tsline.split('"')[3]

            
    
        message = message + '"{}":"{}",'.format("timestamp", ts)
    
        for field in request.headers:
            message = message + '"{}":"{}",'.format(field,request.headers[field].replace('"', "'"))
    
        message = message + '"Body":{}'.format(body[2:-1])
        message = message + "}\n"
        
    else: #BODY ONLY
        message = '{}\n'.format(body[2:-1])
        
    
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
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if "Link" in self.headers:
            msg=StructureNGSILDRequest(self, str(post_data))
        else:
            msg = StructureNGSIv2Request(self, str(post_data), datetime.now())
        #print(msg)
	    
	    
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




