# -*- coding: utf-8 -*-
import socketserver
import json
import time
import re
"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""
u = {}
log = []
class ClientHandler(socketserver.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """
               
    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.possible_request = {
            'login': self.parse_login,
            'logout': self.parse_logout,
            'msg': self.parse_msg,
            'names': self.parse_names,
            'help': self.parse_help,
            # More key:values pairs are needed
        }
        self.d = {}
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096).decode()
            print(json.loads(received_string))
            received = json.loads(received_string)
            self.d = {}
            received['request'] = received['request'].lower()
            print(received)
            if(received['request'] in self.possible_request):
                self.possible_request[received['request']](received)
            else:
                self.response_error("request invalid")
            
            if(received['request'] == 'logout'):
                return 0
            
            # TODO: Add handling of received payload from client
    


    def response_error(self, cont):
        self.d['sender'] = 'server'
        self.d['response'] = "error"
        self.d['content'] = cont
        self.send()
        
    def parse_login(self, data):
        if(self.connection in u.keys()):
            return self.response_error("Already logged in")
            
        if(data['content'] in u.values()):
            return self.response_error("Username taken")
            
        if(data['content'] == "" or not(re.match('[a-zA-Z]*$',data['content']))):
            return self.response_error("Username invalid")
        u[self.connection] = data['content']
        self.d['sender'] = 'server'
        self.d['response'] = 'history'
        self.d['content'] = log
        self.send()
            
    
    def parse_logout(self, data):
        if(self.connection not in u.keys()):
            return self.response_error("Not logged in")
            
        self.d['sender'] = 'server'
        self.d['response'] = 'info'
        self.d['content'] = 'logout successful'
        self.d.pop(u[self.connection], None)
        self.connection.close()
        
        
    def parse_msg(self, data):
        if(self.connection not in u.keys()):
            return self.response_error("Not logged in")
            
        self.d['sender'] = u[self.connection]
        self.d['response'] = 'message'
        self.d['content'] = data['content']
        log.append(json.dumps(self.d))
        self.send()
    
    def parse_names(self, data):
        if(self.connection not in u.keys()):
            return self.response_error("Not logged in")
            
        self.d['sender'] = 'server'
        self.d['response'] = 'info'
        self.send()
    
    def parse_help(self, data):
        h = ("login<username> - login to server\n"+
        "logout - logout of server\n"+
        "msg<message> - Send a message to connected clients\n"+
        "names - list all usernames connected to server\n"+
        "help - show this help text")
        
        self.d['response'] = 'info'
        self.d['content'] = h
        self.d['sender'] = 'server'
        self.send()
    
    def send(self):
        #convert to json and send
        self.d['timestamp'] = time.time()
        payload = json.dumps(self.d)
        self.connection.send(payload.encode())
    

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print ('Server running...')

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
