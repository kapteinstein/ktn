# -*- coding: utf-8 -*-
import json
import datetime

def calculate(string):
    # split the string anc calculate lenght of the words
    o = string.split()
    l = []
    for word in o:
        l.append(len(word))
    return o, l

class MessageParser():
    def __init__(self):
        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'history': self.parse_history,
        }

    def parse(self, payload):
        payload = json.loads(payload) # decode the JSON object

        # print timestamp
        time = datetime.datetime.fromtimestamp(payload['timestamp'])
        print("{}".format(time.strftime('%H:%M:%S')), end='')

        # parse the request
        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            # Response not valid
            print("  vel, ting er messed up. Her er payload:")
            print(payload)

    def parse_error(self, payload):
        # Parse the error message
        print(" {:>10}: {}".format("error", payload['content']))

    def parse_info(self, payload):
        # Parse the info message
        print(" {:>10}: {}".format("info", payload['content']))

    def parse_message(self, payload):
        # Parse the message itself and create a formated string
        # that is (hopefull) shorter than the terminal default window
        string, lengths = calculate(payload['content'])
        counter = 0
        s = ""
        for i in range(len(string)):
            if counter + lengths[i] > 58:
                s += "\n                   : "
                counter = 0
            counter += lengths[i] + 1
            s += string[i] + ' '
        print(" {:>10}: {}".format(payload['sender'], s))

    def parse_history(self, payload):
        # Parse a history-response
        print(" : ============================== History " +
            "==============================")
        for message in payload['content']:
            msg = json.loads(message)
            time = datetime.datetime.fromtimestamp(msg['timestamp'])
            print("{}".format(time.strftime('%H:%M:%S')), end='')
            self.parse_message(msg)
        print("-------- : ===============================" +
                "======================================")
