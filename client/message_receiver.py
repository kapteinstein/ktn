# -*- coding: utf-8 -*-
from threading import Thread

class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """
        # run __init__ because of Python3
        super(MessageReceiver, self).__init__()

        # Flag to run thread as a deamon
        self.daemon = True
        self.client = client
        self.connection = connection

        # TODO: Finish initialization of MessageReceiver
        # start thread
        self.start()

    def run(self):
        # TODO: Make MessageReceiver receive and handle payloads
        while True:
            # recv payload and decode the binary file
            payload = self.connection.recv(4096).decode()
            # send message over to client
            self.client.receive_message(payload)
