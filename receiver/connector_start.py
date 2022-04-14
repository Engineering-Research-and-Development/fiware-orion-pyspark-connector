from connector_lib import *
import conf as connectorconf
import NGSIV2_primer as NGSI




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


