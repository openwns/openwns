#!/usr/bin/python
import SimpleHTTPServer
import SocketServer

# minimal web server.
# serves files from current directory

PORT = 8000

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
