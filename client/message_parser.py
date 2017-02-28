# -*- coding: utf-8 -*-
import json
class MessageParser():
    def __init__(self):

        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'history': self.parse_history,
            'success': self.parse_success,
            # More key:values pairs are needed
        }

    def parse(self, payload):
        payload = json.loads(payload) # decode the JSON object

        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']](payload)
        else:
            print("vel, ting er messed up. Her er payload:")
            print(payload)
            # Response not valid

    def parse_error(self, payload):
        pass

    def parse_info(self, payload):
        pass

    def parse_message(self, payload):
        pass

    def parse_history(self, payload):
        pass

    def parse_success(self, payload):
        # prints success if message received from server
        print("success :D")

    # Include more methods for handling the different responses...
