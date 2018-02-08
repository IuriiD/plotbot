import os
import json
from flask import Flask, request, make_response, jsonify
import pygal
import cairosvg

app = Flask(__name__)

# ###################### Functions ##############################

def pygal_bar_chart(data, png_file_name, chart_name):
    bar_chart = pygal.Bar()             # Then create a bar graph object
    bar_chart.add(chart_name, data)     # Add some values
    bar_chart.render_to_png(png_file_name)
    return True

def mysplit(txt, seps):
    # split input string by a list of possible separators, for eg. '4 - 4  5/ 5,6' >> ['4', '4', '5', '5', '6']
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split()]

def get_data(mychartdata, ds_key):
    # function takes the name of data series (for eg., 'data-series-1.original') and json from webhook
    # ('result' >> 'contexts'['mychart'] >> 'parameters') and returns a dictionary containing
    # a name of this data series and corresponding numbers in format {'data-series-1.original_name': 'B', 'data-series-1.original_data': [2.0, 4.0, 5.0, 6.0, 6.0]}
    # in case of invalid input (no numbers) - returns error flag
    ds_data = []
    ds_name = ''
    result_code = 'ok'
    ds = mychartdata[ds_key]

    # user is supposed to have entered smth like 'series C: 4, 4, 5, 5,6' or '4, 4, 5, 5,6' (all ok)
    # but he/she may have entered invalid (non-digit) values  like 'sdsdfsd sddd' or ',, ,,, ,'

    # try to split this string by ':"
    # possible results:
    # 1. input doesn't contain ':' - we'll get a list with 1 value to validate for data series (numbers) // '4, 4, 5, 5', ' ', 'sdfsdfsdf sdsdds'
    # 1.1 also user may have forgotten to enter ':' in a valid input, for eg. 'series C 4, 4, 5, 5,6' or 'series-500 4, 4, 5, 5,6' - for now this variant will be considered invalid but later
    # some logics may be added to recognise it as valid
    # 2. input contains 1 ':' - we'll get a list with 2 values, the 1st - ds name, the 2nd - ds data // 'series C: 4, 4, 5, 5,6', 'sdfsdf: sddd', ':'
    # 3. input contains >1 ':' - we'll get a list with >2 values, the 1st will be ds name, the 2nd - ds data, all the rest will be discarded // 'series C: 4, 4, 5, 5,6 'series D: 1, 2, 3, 5,3'
    ds_splitted = ds.split(':')
    if len(ds_splitted) == 1:
        ds_data_part = mysplit(ds_splitted[0].strip(), [' ', ',', ';', '-', '/'])
    else:
        ds_name_part = ds_splitted[0].strip() # any values including empty
        ds_data_part = mysplit(ds_splitted[1].strip(), [' ', ',', ';', '-', '/'])

    # so we have a part supposed to be data series. variants:
    # 1. correct data ('4', '4', '5', '5', '6') - result code 'ok'
    # 2. completely incorrect data (''; 'sdsdd', 'sds') - result code 'bad'
    # 3. partly correct data ('sdfs', '4.0', '2.3', 'ssdsd') - results code 'partly'
    # we'll try to convert these data to float numbers, all nondigit values will be substituted with 0
    # in case all series contains only 0s (valid 0s or nondigit values substituted with 0) - result code 'bad'
    for item in ds_data_part:
        if item.isdigit():
            ds_data.append(float(item))
        else:
            ds_data.append(0)
            result_code = 'partly'

    ds_sum = 0
    for x in ds_data:
        ds_sum += x

    if ds_sum == 0:
        result_code = 'bad'

    # so now we have variants with result codes:
    # 1. 'ok' = valid numbers with or without ds name >> Alright! $data-series-0.original for our #mychart.bar-chart-styles #mychart.chart-types received. Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh
    # 2. 'partly' = at least some (1) numbers with or without ds name >> Some errors were found in your data. After replacing errors with 0, your data series will look like ... . Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? You can also start afresh (write 'restart')
    # 3. 'bad' = no numbers (ds name doesn't matter) >> Invalid data series. Please enter correct data in format 'Series name (optionally): series data', for eg. 'Fibonacci: 1, 2, 4, 8, 16, 32'
    # p.s. some additional data for response compilation - chart type and subtype
    # We'll return [result_code][message][validated_data_series as dictionary {ds_name: ds_data}]
    chart_type = mychartdata['chart-types']
    chart_subtype = mychartdata['bar-chart-styles']
    if result_code == 'ok':
        output = [
            'ok',
            "Alright! Series " + ds + " for our " + chart_subtype + " " + chart_type + " received. Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh",
            {ds_name_part: ds_data}
        ]
    elif result_code == 'partly':
        output = [
            'partly',
            "Some errors were found in your data. After replacing those errors with 0, the data series will look like '" + ds_name_part + ": " + str(ds_data) + "'. Start afresh (write 'restart'), add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or draw a chart?",
            {ds_name_part: ds_data}
            ]
    else:
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'Series name (optionally): series data', for eg. 'Fibonacci: 1, 2, 4, 8, 16, 32'",
            {}
            ]

    return output

# ###################### Functions END ##############################

# ###################### Decorators ##############################

@app.route('/')
def index():
    return 'Food Composition Chatbot'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(silent=True, force=True)
    action = req.get('result').get('action')
    print('Webhook received: ' + str(req))

    # Check if the request is for the foodcomposition action
    if action == 'foodcomposition':

        res = {
            'speech': 'foodcomposition',
            'displayText': 'foodcomposition',
            'contextOut': req['result']['contexts']
        }


    elif action == 'data-series-0':
        #  get 'contexts'
        contexts = req.get('result').get('contexts')

        # from the 1st context (supposed to be 'mychart') get 'parameters'
        mychartdata = contexts[0].get('parameters')

        # get and try to parse and validate data series, in case it's invalid - return error message
        validation_result = get_data(mychartdata, 'data-series-0.original')

        # Compose the response to dialogflow.com
        # Depending on validation results we need to update contexts
        # After triggering 'add-series-XX' intent in DF a context 'ready2plot' is created which allows to proceed to plotting
        # If data entered by user is invalid and if no previous valid data exists in context 'mychart' in key 'validated_ds'
        # then lifespan for 'ready2plot' context should be set to 0 (no plotting allowed until at least 1 valid DS is entered)
        # If this is the 1st time that this validation webhook is triggered - create a key 'validated_ds' in context 'mychart'
        # and save validated DS in it

        # get existing contexts
        outputcontext = contexts
        print('Old contexts: ' + str(outputcontext))

        if validation_result[0] == 'ok' or validation_result[0] == 'partial':
            print('Here1')
            for context in outputcontext:
                if context['name'] == 'mychart':
                    if 'validated_ds' in context['parameters']:
                        print('Here2')
                        context['parameters']['validated_ds'].append(validation_result[2])
                else:
                    print('Here3')
                    context['parameters'].update({'validated_ds': [validation_result[2]]})
        else:
            print('Here4')
            for context in outputcontext:
                if context['name'] == 'mychart':
                    if not context['parameters']['validated_ds']:
                        print('Here5')
                        for anothercontext in outputcontext:
                            if anothercontext['name'] == 'ready2plot':
                                anothercontext['lifespan'] = 0

        print('New contexts: '+ str(outputcontext))

        res = {
            'speech': validation_result[1],
            'displayText': validation_result[1],
            'contextOut': outputcontext
        }


    # Check if the request is for the plotbot action
    elif action == 'plotbot':
        contexts = req.get('result').get('contexts')
        chart_data2split = contexts[0].get('parameters').get('chart-data.original')
        chart_data = split(chart_data2split, [' ', ',', ';', '-', '/'])


        #pygal_bar_chart(chart_data,'test.png', 'test chart')

        print(req)
        print('************************')
        print(action)
        print('************************')
        print('chart_data: {}, type: {}.'.format(chart_data, type(chart_data)))

        # Compose the response to dialogflow.com
        res = {
            'speech': str(chart_data),
            'displayText': str(chart_data),
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
    port = int(os.getenv('PORT', 5000)) # for Heroku, otherwise we get "Error R10 (Boot timeout) -> Web process failed to bind to $PORT within 60 seconds of launch" ; solution: https://jamesmcfadden.co.uk/heroku-web-process-failed-to-bind-to-port-within-60-seconds-of-launch
    app.run(debug=False, host='0.0.0.0', port=port)


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
