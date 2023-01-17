#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Justin Boileau
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

ALLOWED_CONTENT_TYPES: list[str] = ['text/html', 'text/css']

ALLOWED_METHODS: list[str] = ['GET']

def get_request_parts(request: str):
    """
    Parse a dictionary of request details from request data

    Note: We could also get the other request headers here but
    they aren't needed for this assignment
    """

    # Get a list of values from the first line in the request
    details = request.split("\r\n")[0].split()
    
    if len(details) == 3:
        # Get request method, path, and protocol
        method, path, protocol = details
        return {
            'method': method,
            'path': path,
            'protocol': protocol,
        }
    else:
        return None

def decide_content_type(path: str):
    """
    Decide content MIME type based on path string. Defaults to text/plain.
    """
    if path.endswith('.html'):
        return 'text/html'
    elif path.endswith('.css'):
        return 'text/css'
    else:
        return 'text/plain'

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        # Get request details
        parts = get_request_parts(self.data.decode('utf-8'))
        if parts is None:
            return
        
        path = os.getcwd() + '/www' + parts['path']
        
        # Check if computed path is within the /www directory
        if (os.getcwd() + '/www') not in os.path.normpath(path):
            self.respond_not_found()
            return

        # Check if method is valid
        if parts['method'] not in ALLOWED_METHODS:
            self.respond_method_not_allowed()
            return

        if os.path.isfile(path):
            # Check if file exists

            # Response with OK and the file if it exists
            with open(path) as f:
                self.respond_ok(decide_content_type(path), f.read())

        elif os.path.isdir(path):
            # Check if directory exists

            if path.endswith('/'):
                # New path with index.html
                path = path + 'index.html'
                if os.path.exists(path):
                    # Send index.html if it exists
                    with open(path) as f:
                        self.respond_ok('text/html', f.read())
                else:
                    # Send 404 if there is no index.html in the directory
                    self.respond_not_found()
            else:
                # Respond with 301 to path + / if that path does exist
                self.respond_moved(parts['path'] + '/')
        else:
            # Send 404 if path did not exist
            self.respond_not_found()
            

    def respond_ok(self, content_type: ALLOWED_CONTENT_TYPES, content: str | bytearray):
        """
        Respond with HTTP 200 and some content
        """
        
        # Ensure valid content type
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f'value of content_type arguement must be one of {ALLOWED_CONTENT_TYPES}')

        # Convert str to bytearray or throw error if content is not one already
        if isinstance(content, str):
            content = bytearray(content, 'utf-8')
        elif not isinstance(content, bytearray):
            raise TypeError(f'content must of type str or bytearray')

        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n", 'utf-8'))
        self.request.sendall(bytearray(f"Content-Type: {content_type}\r\n\r\n", 'utf-8'))
        self.request.sendall(content)

    def respond_moved(self, moved_to: str):
        """
        Respond with HTTP 301 and provide the new location
        """
        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n", 'utf-8'))
        self.request.sendall(bytearray(f"Location: {moved_to}\r\n", 'utf-8'))

    def respond_not_found(self):
        """
        Respond with HTTP 404 and a notice page
        """
        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n",'utf-8'))
        self.request.sendall(bytearray("Content-Type: text/html\r\n\r\n", 'utf-8'))
        self.request.sendall(bytearray(f"<html><b>404 Not Found</b></html>\r\n", 'utf-8'))

    def respond_method_not_allowed(self):
        """
        Respond with HTTP 405 and a notice page
        """
        self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n",'utf-8'))
        self.request.sendall(bytearray("Content-Type: text/html\r\n\r\n", 'utf-8'))
        self.request.sendall(bytearray(f"<html><b>405 Method Not Allowed</b></html>\r\n", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
