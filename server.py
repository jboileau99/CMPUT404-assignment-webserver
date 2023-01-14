#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

'''
TODO (There's other but this is just things I think of and don't want to forget)
** CHECK REQUIREMENTS.ORG **

- Only server from /www ... does this mean consider paths as www/ + path?? I think so, check unit tests
'''


def get_request_parts(request: str):
    """
    Parse a dictionary of request details from request data
    """

    lines = request.split("\r\n")

    # Get request method, path, and protocol from first element
    method, path, protocol = lines[0].split(maxsplit=3)

    # Get request headers from remaining elements
    headers = {}
    for line in lines[1:]:
        k, v = line.split(':', maxsplit=1)  # maxsplit=1 ensures lines like 'Host: 127.0.0.1:8080' won't split twice
        headers[k.strip()] = v.strip()

    return {
        'method': method,
        'path': path,
        'protocol': protocol,
        'headers': headers
    }

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)

        # Get request path and headers
        parts = get_request_parts(self.data.decode('utf-8'))
        path: str = os.getcwd() + parts['path']
        print(path)

        # Check if path exists
        if os.path.isfile(path):

            print('is file')

            # Response with OK and the file if it exists
            self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n", 'utf-8'))
            self.request.sendall(bytearray("Content-Type: text/html\r\n", 'utf-8'))
            with open(path) as f:
                self.request.sendall(bytearray(f.read(),'utf-8'))

        elif os.path.isdir(path):

            print('is dir')

            if path.endswith('/'):

                # New path with index.html
                path = path + 'index.html'
                if os.path.exists(path):

                    # Send index.html if it exists
                    self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n", 'utf-8'))
                    self.request.sendall(bytearray("Content-Type: text/html\r\n", 'utf-8'))
                    with open(path) as f:
                        self.request.sendall(bytearray(f.read(),'utf-8'))
                else:

                    # Send 404 if there is no index.html in the directory
                    self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n",'utf-8'))
                    self.request.sendall(bytearray("Content-Type: text/html\r\n\r\n", 'utf-8'))
                    self.request.sendall(bytearray(f"<html><b>404 Not Found</b></html>\r\n", 'utf-8'))

            else:
                # Respond with 301 to path + / if that path does exist
                self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n", 'utf-8'))
                self.request.sendall(bytearray(f"Location: {parts['path']}/\r\n", 'utf-8'))

        else:
            # Send 404 if path did not exist
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n",'utf-8'))
            self.request.sendall(bytearray("Content-Type: text/html\r\n\r\n", 'utf-8'))
            self.request.sendall(bytearray(f"<html><b>404 Not Found</b></html>\r\n", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
