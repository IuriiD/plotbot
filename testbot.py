# this is the webhook for a testbot

import os
import json
import requests
from flask import Flask, request, make_response, jsonify
from keys import nutrionix_app_id, nutrionix_app_key
import pygal
from pygal.style import DefaultStyle
import cairosvg

app = Flask(__name__)

# ###################### Decorators ##############################
@app.route('/')
def index():
    return 'Food Composition Chatbot'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(silent=True, force=True)
    action = req.get('result').get('action')

    # TestBot Webhook action - testing stuff
    if action == 'testbot':
        myinput = req.get('result').get('parameters').get('input')

        res = {
            'speech': '### 1 ###: ' + myinput,
            'displayText': '### 2 ###: ' + myinput,
            'source': 'mywebhook',
            "messages": [
                {
                    "speech": "Hello Telegram: " + myinput,
                    "platform": "telegram",
                    "type": 0
                },
                {
                    "imageUrl": "https://iuriid.github.io/img/chart.types.jpg",
                    "platform": "telegram",
                    "type": 3
                },
                {
                    "buttons": [
                        {
                            "postback": "line",
                            "text": "Line"
                        },
                        {
                            "postback": "bar",
                            "text": "Bar"
                        },
                        {
                            "postback": "scatter",
                            "text": "Scatter"
                        },
                        {
                            "postback": "pie",
                            "text": "Scatter"
                        }
                    ],
                    "imageUrl": "https://iuriid.github.io/img/chart.types.jpg",
                    "platform": "telegram",
                    "title": "Please choose a chart type",
                    "type": 1
                },
                {
                    "speech": 'Response for web demo: ' + myinput,
                    "type": 0
                }
            ]
        }

    else:
        # If the request is not of our actions throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    return make_response(jsonify(res))
# ###################### Decorators END ##############################

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0')#, port=port)