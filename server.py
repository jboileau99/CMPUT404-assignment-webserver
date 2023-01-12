#  coding: utf-8 
import socketserver

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
        print(line)
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
        print ("Got a request of: %s\n" % self.data)

        # Get request path and headers
        print(get_request_parts(self.data.decode('utf-8')))

        self.request.sendall(bytearray("OK",'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
