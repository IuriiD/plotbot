import os
import json
from flask import Flask, request, make_response, jsonify
import pygal
import cairosvg

app = Flask(__name__)

# ###################### Plotbot Functions ##############################

def pygal_bar_chart(data, png_file_name):
    bar_chart = pygal.Bar()
    for ds in data:
        for key, value in ds.items():
            bar_chart.add(key, value)
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
        ds_data_part = mysplit(ds_splitted[0].strip(), [' ', ',', ';', '- ', '/'])
    else:
        ds_name = ds_splitted[0].strip() # any values including empty
        ds_data_part = mysplit(ds_splitted[1].strip(), [' ', ',', ';', '- ', '/'])

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

    # we also need to ckeck for previous validated series to display them to user
    if result_code == 'ok':
        output = [
            'ok',
            "Alright! Series '" + ds + "' for our " + chart_subtype + " " + chart_type + " received. Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh",
            {ds_name: ds_data}
        ]
    elif result_code == 'partly':
        output = [
            'partly',
            "Some errors were found in your data. After replacing those errors with 0, the data series will look like '" + ds_name + ": " + str(ds_data) + "'. Start afresh (write 'restart'), add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or draw a chart?",
            {ds_name: ds_data}
            ]
    else:
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'Series name (optionally): series data', for eg. 'Fibonacci: 1, 2, 4, 8, 16, 32'",
            {}
            ]

    return output

# ###################### Plotbot Functions END ##############################

# ###################### Decorators ##############################

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
        foodlabel = []
        # Get food to be analysed
        foodlabel.append(req.get('result').get('parameters').get('food'))

        # Make request to Nutritionix API and get fats/carbohydrates/proteins %
        nutr_percent = nutrionix_requests(foodlabel)['average_percents']
        output = '{} contains {}% of fats, {}% of carbohydrates and {}% of proteins'.format(foodlabel[0], nutr_percent[0], nutr_percent[1], nutr_percent[2])
        print(output)

        # Compose the response to dialogflow.com
        res = {
            'speech': output,
            'displayText': output,
            'contextOut': req['result']['contexts']
        }

    elif action == 'testbot':
        myinput = req.get('result').get('parameters').get('inputdata'))

        res = {
            'speech': 'http://35.196.100.14/static/test.png',
            #'displayText': 'http://35.196.100.14/static/test.svg',
            'messages': [
                {
                    "speech": 'Here must be image URL - https://iuriid.github.io/img/fc-1.jpg',
                    'type': 0,
                    'platform': 'telegram'
                },
                {
                    "type": 1,
                    "platform": "telegram",
                    "imageUrl": "https://iuriid.github.io/img/fc-1.jpg"
                },
                {
                    "speech": 'Here must be image URL - https://iuriid.github.io/img/fc-1.jpg',
                    'type': 0,
                }
            ],
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
        # print('Old contexts: ' + str(outputcontext))

        # store validated data series in context ('mychart' >> 'parameters' >> 'validated_ds')
        if validation_result[0] == 'ok' or validation_result[0] == 'partly':
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
            # if input was invalid and no previous validated DS exist in contexts, context 'ready2plot' should be deleted ('lifespan' >> 0)
            print('Here4')
            for context in outputcontext:
                if context['name'] == 'mychart':
                    if not 'validated_ds' in context['parameters']:
                        print('Here5')
                        for anothercontext in outputcontext:
                            if anothercontext['name'] == 'ready2plot':
                                anothercontext['lifespan'] = 0

        # print('New contexts: '+ str(outputcontext))

        res = {
            'speech': validation_result[1],
            'displayText': validation_result[1],
            'contextOut': outputcontext
        }


    # Check if the request is for the plotbot action
    elif action == 'plotbot':
        # at this stage we have at least 1 already validated data series saved in context 'mychart' in key 'validated_ds'
        contexts = req.get('result').get('contexts')
        for context in contexts:
            if context['name'] == 'mychart':
                data2plot = context['parameters']['validated_ds'] # is a list for eg. [{"fibo": [1, 2, 4, 8]}, {"next": [2, 3, 4, 5]}]

        pygal_bar_chart(data2plot,'static/test.png')

        # then we need to return this image's ULR and also update contexts (set lifespan for mychart and ready2chart to 0)
        for context in contexts:
            if context['name'] == 'mychart' or context['name'] == 'ready2plot':
                context['lifespan'] = 0

        # Compose the response to dialogflow.com
        res = {
            'speech': 'http://35.196.100.14/static/test.png',
            #'displayText': 'http://35.196.100.14/static/test.svg',
            'messages': [
                {
                    "speech": 'Here must be image URL - http://35.196.100.14/static/test.png',
                    'type': 0,
                    'platform': 'telegram'
                },
                {
                    "type": 1,
                    "platform": "telegram",
                    "imageUrl": "http://35.196.100.14/static/test.png"
                },
                {
                    "speech": 'Here must be image URL - http://35.196.100.14/static/test.png',
                    'type': 0,
                },
                {
                    "type": 1,
                    "platform": "facebook",
                    "imageUrl": "http://35.196.100.14/static/test.png"
                },
                {
                    "speech": 'Here must be image URL - http://35.196.100.14/static/test.png',
                    'type': 0,
                    'platform': 'facebook'
                }
            ],
            'contextOut': contexts
        }

    else:
        # If the request is not of our actions throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    return make_response(jsonify(res))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) # for Heroku, otherwise we get "Error R10 (Boot timeout) -> Web process failed to bind to $PORT within 60 seconds of launch" ; solution: https://jamesmcfadden.co.uk/heroku-web-process-failed-to-bind-to-port-within-60-seconds-of-launch
    app.run(debug=False, host='0.0.0.0', port=port)