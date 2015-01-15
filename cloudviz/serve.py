#!/usr/bin/env python

from BaseHTTPServer import HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler

handler = CGIHTTPRequestHandler
handler.cgi_directories = ['/cgi-bin']
server = HTTPServer(('0.0.0.0', 8123), handler)
server.serve_forever()
