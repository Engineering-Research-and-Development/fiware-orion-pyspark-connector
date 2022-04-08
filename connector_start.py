from connector_lib import *
import conf as connectorconf




socket_address = (connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
s.bind(socket_address)



threadsocket = SocketThread(s, socket_address)
threadsocket.start()


server_address = (connectorconf.HTTPADDRESS, connectorconf.HTTPPORT)
print(server_address)


httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)



threadserver = ServerThread(httpd)
threadserver.start()




######################################################################



conf = SparkConf().setAppName("TextPicker").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)
ssc = StreamingContext(sc, 10)


record = ssc.socketTextStream(connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT, storageLevel=StorageLevel.MEMORY_AND_DISK_2)


l = record.map(lambda x: ParseToNGSIv2(x))

