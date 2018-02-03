import os
import json
import requests
from flask import Flask, request, make_response, jsonify
from keys import nutrionix_app_id, nutrionix_app_key
import pygal
import cairosvg

app = Flask(__name__)

def pygal_bar_chart(data, png_file_name, chart_name):
    bar_chart = pygal.Bar()             # Then create a bar graph object
    bar_chart.add(chart_name, data)     # Add some values
    bar_chart.render_to_png(png_file_name)
    return True

@app.route('/')
def index():
    return 'Food Composition Chatbot'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(silent=True, force=True)
    action = req.get('result').get('action')

    # Check if the request is for the foodcomposition action
    if action == 'foodcomposition':

        res = {
            'speech': 'foodcomposition',
            'displayText': 'foodcomposition',
            'contextOut': req['result']['contexts']
        }

    # Check if the request is for the plotbot action
    elif action == 'plotbot':
        contexts = req.get('result').get('contexts')
        chart_data = list(contexts[0].get('parameters').get('chart-data.original'))

        pygal_bar_chart(chart_data,'test.png', 'test chart')

        print(req)
        print('************************')
        print(action)
        print('************************')
        print(chart_data)

        # Compose the response to dialogflow.com
        res = {
            'speech': 'Done',
            'displayText': 'Done',
            'contextOut': req['result']['contexts']
        }

    else:
        # If the request is not to the foodcomposition action throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    return make_response(jsonify(res))

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0')#, port=port)


'''
import os
from flask import Flask, render_template, url_for, request, redirect, flash, make_response, jsonify
import pygal
import cairosvg

app = Flask(__name__)

chart_name = 'Fibonacci'
data = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
png_file_name = 'bar_chart1.png'

def pygal_bar_chart(data, png_file_name, chart_name):
    bar_chart = pygal.Bar()             # Then create a bar graph object
    bar_chart.add(chart_name, data)     # Add some values
    bar_chart.render_to_png(png_file_name)
    return True

@app.route('/')
def index():
    return 'PlotBot'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(silent=True, force=True)
    action = req.get('result').get('action')

    # Check if the request is for the plotbot action
    if action == 'plotbot':
        contexts = req.get('result').get('contexts')
        chart_data = list(contexts[0].get('parameters').get('chart-data.original'))

        pygal_bar_chart(chart_data,'test.png', 'test chart')

        print(req)
        print('************************')
        print(action)
        print('************************')
        print(chart_data)

        # Compose the response to dialogflow.com
        res = {
            'speech': 'Done',
            'displayText': 'Done',
            'contextOut': req['result']['contexts']
        }

    else:
        # If the request is not to the translate.text action throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    return make_response(jsonify(res))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) # for Heroku, otherwise we get "Error R10 (Boot timeout) -> Web process failed to bind to $PORT within 60 seconds of launch" ; solution: https://jamesmcfadden.co.uk/heroku-web-process-failed-to-bind-to-port-within-60-seconds-of-launch
    app.run(debug=False, host='0.0.0.0', port=port)


{'originalRequest': {
    'source': 'telegram',
    'data': {
        'update_id': 58256141,
        'message': {
            'date': 1517669399,
            'chat': {
                'last_name': 'D.',
                'id': 178180819,
                'type': 'private',
                'first_name': 'Iurii'
            },
            'message_id': 66,
            'from': {
                'language_code': 'ru-RU',
                'last_name': 'D.',
                'id': 178180819,
                'is_bot': False,
                'first_name': 'Iurii'
            },
            'text': 'yes'}
    }
},
    'id': '67ec4b54-85d7-4a3e-b235-54e9a4adb6fc',
    'timestamp': '2018-02-03T14:49:59.141Z',
    'lang': 'en',
    'result': {
        'source': 'agent',
        'resolvedQuery': 'yes',
        'speech': '',
        'action': 'plotbot',
        'actionIncomplete': False,
        'parameters': {},
        'contexts': [
            {
                'name': 'draw-chart',
                'parameters': {
                    'chart-name': '',
                    'chart-name.original': '',
                    'chart-data.original': '50 30 20',
                    'chart-types': 'pie chart',
                    'chart-types.original': 'pie',
                    'chart-data': ['50 30 20']
                }, 'lifespan': 5},
            {
                'name': 'generic',
                'parameters': {
                    'chart-name': '',
                    'chart-name.original': '',
                    'chart-data.original': '50 30 20',
                    'telegram_chat_id': '178180819',
                    'chart-types': 'pie chart',
                    'chart-types.original': 'pie',
                    'chart-data': ['50 30 20']
                },
                'lifespan': 0}
        ],
        'metadata': {
            'intentId': '64a55906-39f4-429c-82d7-72f17c50a6b7',
            'webhookUsed': 'true',
            'webhookForSlotFillingUsed': 'false',
            'intentName': "draw.chart - answer 'Yes'"
        },
        'fulfillment': {
            'speech': "Ok. Let's try to draw it.. So we will draw a pie chart using values [50 30 20]",
            'messages': [
                {
                    'type': 0, 'speech': "Ok. Let's try to draw it.. So we will draw a pie chart using values [50 30 20]"}
            ]
        },
        'score': 0.7512499895834375
    },
    'status': {
        'code': 200,
        'errorType': 'success',
        'webhookTimedOut': False
    },
    'sessionId': '1b949e36-c073-42a2-bd9a-c6a93f4ff80f'
}


'''
