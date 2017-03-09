# -*- coding: utf-8 -*-
import socketserver
import json
import time
import re
"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

room = {'main': {'u': {}, 'log': [] }}
usernames = []

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
            'room': self.parse_room,
            'join': self.parse_join,
            'leave': self.parse_leave,
        }

        self.d = {}
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        self.room = 'main'
        self.userName = ''

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096).decode()
            try:
                received = json.loads(received_string)
            except:
                self.parse_logout()
                return 0

            self.d = {}
            received['request'] = received['request'].lower()
            if(received['request'] in self.possible_request):
                self.possible_request[received['request']](received)
            else:
                self.response_error("request invalid")

            if(received['request'] == 'logout'):
                return 0

    def response_error(self, cont):
        self.d['sender'] = 'server'
        self.d['response'] = "error"
        self.d['content'] = cont
        self.send()

    def parse_login(self, data):
        if(self.connection in room[self.room]['u'].keys()):
            return self.response_error("Already logged in")

        if(data['content'] in usernames):
            return self.response_error("Username taken")

        if(data['content'] == "" or not(re.match('[a-zA-Z0-9]*$', data['content']))):
            return self.response_error("Username invalid")

        room['main']['u'][self.connection] = data['content']
        self.d['sender'] = 'server'

        self.d['response'] = 'info'
        self.d['content'] = 'login successful'
        self.send()

        self.d['response'] = 'history'
        self.d['content'] = room[self.room]['log']
        self.userName = data['content']
        usernames.append(self.userName)
        self.send()

    def parse_logout(self, data = None, user = None):
        if(self.connection not in room[self.room]['u'].keys()):
            return self.response_error("Not logged in")

        self.d['sender'] = 'server'
        self.d['response'] = 'info'
        self.d['content'] = 'logout successful'
        if user == None:
            user = self.connection
        room[self.room]['u'].pop(user, None)
        usernames.remove(self.userName)
        user.close()

    def parse_msg(self, data):
        self.d['response'] = 'message'
        self.d['content'] = data['content']
        self.d['timestamp'] = time.time()
        self.d['sender'] = self.userName

        if(self.userName == ''):
            return self.response_error("Not logged in")

        room[self.room]['log'].append(json.dumps(self.d))
        self.send()

    def parse_names(self, data):
        if(self.connection not in room[self.room]['u'].keys()):
            return self.response_error("Not logged in")
        s = ""
        for l in usernames.values():
            s += (l+" ")
        self.d['content'] = s
        self.d['sender'] = 'server'
        self.d['response'] = 'info'
        self.send()

    def parse_help(self, data):
        h = ("\nlogin<username> - login to server\n"+
        "logout - logout of server\n"+
        "msg<message> - Send a message to connected clients\n"+
        "names - list all usernames connected to server\n"+
        "room create/close <name> - create or close a chat room\n" +
        "room list - list rooms\n" +
        "join <name> - join chat room <name>\n"+
        "leave - leave current chat room\n"+
        "help - show this help text")

        self.d['response'] = 'info'
        self.d['content'] = h
        self.d['sender'] = 'server'
        self.send()

    def send(self):
        #convert to json and send
        self.d['timestamp'] = time.time()
        payload = json.dumps(self.d)
        disconnected = []
        if self.d['response'] == 'message':
            for user in room[self.room]['u'].keys():
                try:
                    user.send(payload.encode())
                except:
                    disconnected.append(user)
            for user in disconnected:
                self.parse_logout('', user)
        else:
            self.connection.send(payload.encode())

    def parse_room(self, data):
        """
        desired functionality:
          - create <name>: create chatroom <name>, userlist and log
          - close <name> : close room and remove history
        """
        if(self.connection not in room[self.room]['u'].keys()):
            return self.response_error("Not logged in")

        # hacky solution to avoid crashes
        c = []
        c = data['content'].lower().split()
        if len(c) < 2:
            c.append('')

        # parse the different requests
        if (c[0] == 'create'):
            if (c[1] == ''):
                return self.response_error("Spesify name, 'room create <name>'")

            if (c[1] in room.keys()):
                return self.response_error("Room '{}' exist".format(c[1]))

            room[c[1]] = {'u': {}, 'log': []}
            self.d['content'] = "chat room '{}' created.".format(c[1])

        elif (c[0] == 'close'):
            if (c[1] not in room.keys()):
                return self.response_error("Room does not exist")

            if (room[c[1]]['u'] != {}):
                self.d['content'] = "Can't close room. Users are still there."
            else:
                room.pop(c[1], None)
                self.d['content'] = "Chat room '{}' closed".format(c[1])

        elif (c[0] == 'list'):
            s = ""
            for r in room.keys():
                s += r + ' '
            self.d['content'] = s

        else:
            self.d['content'] = ("\nUsage: \n"+
                "room create/close <name> - create or close a chat room\n"+
                "room list - list rooms\n"+
                "join <name> - join chat room <name>\n"+
                "leave - leave current chat room")

        self.d['response'] = 'info'
        self.d['sender'] = 'server'
        self.send()

    def parse_join(self, data):
        """ join <room> : join a chat room """
        # add user to list at room['name']
        if(self.connection not in room[self.room]['u'].keys()):
            return self.response_error("Not logged in")

        c = data['content'].lower()

        if (c not in room.keys()):
            return self.response_error("Room '{}' does not exist".format(c))

        # remove user from current room and add to a new
        room[self.room]['u'].pop(self.connection, None)
        room[c]['u'][self.connection] = self.userName

        # send the rooms log to user after join
        self.d['response'] = 'history'
        self.d['content'] = room[c]['log']
        self.room = c
        self.send()

    def parse_leave(self, data):
        """ leave current chatroom and join the default 'main' room"""
        if(self.connection not in room[self.room]['u'].keys()):
            return self.response_error("Not logged in")

        if (self.room == 'main'):
            return self.response_error("You are currently not in a chat room")

        # remove user from current room and add to main
        room[self.room]['u'].pop(self.connection, None)
        room['main']['u'][self.connection] = self.userName

        # send main's log
        self.d['response'] = 'history'
        self.d['content'] = room['main']['log']
        self.room = 'main'
        self.send()

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
    HOST, PORT = '', 9998
    print ('Server running...')

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
