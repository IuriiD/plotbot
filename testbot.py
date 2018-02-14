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
        myinput = req.get('result').get('parameters').get('inputdata')

        res = {
            'speech': '1 https://iuriid.github.io/img/fc-2.jpg',
            'displayText': '2 https://iuriid.github.io/img/fc-2.jpg',
            'source': 'mywebhook',
            # messages for web demo
            'messages': [
                {
                    'type': 3, # image
                    'platform': 'telegram',
                    'imageUrl': 'https://iuriid.github.io/img/fc-2.jpg'
                },
                {
                    'type': 0, # text
                    'platform': 'telegram',
                    'speech': '4 Hello'
                },
                {
                    'type': 3,
                    'platform': 'facebook',
                    'imageUrl': 'https://iuriid.github.io/img/fc-1.jpg'
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

    '''
            'speech': 'Response1',
            'displayText': 'Response2',
            
            "data": {
                "telegram": {
                        "photo": "https://iuriid.github.io/img/fc-2.jpg"
                }
            },    
    '''

''',
# messages for Facebook, Telegram etc
"data": {
    "facebook": [
        {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": 'http://35.196.100.14/' + ourfilename + '.png'
                }
            }
        },
        {
            "text": 'And here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg'
        },
        {
            "text": 'To make another chart type "draw chart" or "restart"'
        }
    ],
    "telegram": [
        {
            "photo": 'https://iuriid.github.io/img/fc-2.jpg'
        },
        {
            "text": '5 https://iuriid.github.io/img/fc-2.jpg'
        },
        {
            "text": '6 https://iuriid.github.io/img/fc-2.jpg'
        }
    ]
}'''