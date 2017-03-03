# -*- coding: utf-8 -*-
import socket
from message_receiver import MessageReceiver
from message_parser import MessageParser
import json
from sys import argv

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.server_port = server_port
        self.parser = MessageParser()

        self.run()

    def run(self):
        # Initiate the connection to the server and receiver
        self.connection.connect((self.host, self.server_port))
        print("-------- : Connected to host: {}".format(self.host))
        MessageReceiver(self, self.connection)
        d = {}  # new dictonary

        while True:
            # get message from user
            message = input().split(' ', 1)
            d['request'] = message[0]
            try:
                d['content'] = message[1]
            except:
                # empty content
                d['content'] = ''

            payload = json.dumps(d)     # convert to json
            self.send_payload(payload)  # send payload

            if d['request'] == 'logout':
                return self.disconnect()

    def disconnect(self):
        # Handle disconnect
        self.connection.close()
        print("Disconnected")
        return 0

    def receive_message(self, message):
        # Handle incoming message
        self.parser.parse(message)

    def send_payload(self, data):
        # Handle sending of a payload
        self.connection.send(data.encode())


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    try:
        host = argv[1]
    except:
        host = 'localhost'

    client = Client(host, 9998)
