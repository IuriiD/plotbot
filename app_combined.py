import os
import json
import requests
from flask import Flask, request, make_response, jsonify
from keys import nutrionix_app_id, nutrionix_app_key
import pygal
import cairosvg

app = Flask(__name__)

def nutrionix_requests(label_list):
    ''' Function takes a list of products' labels got using Google Vision API or a label submitted by user and for [products_n] products (in case of user's label products_n=1)
        from this list tries to find foods in Nutrionix DB.
        For each food product (for eg., 'sausage') [how_many_terms] quantity of items are requested (for eg., items 'Sausage, Peppers and Onions - 1 serving', 'Sausage - 2, links' for a term 'sausage)
        For each food item (for eg., 'Sausage - 2, links') id, name, [relevance] score and abs. quantity (in grams) of fats, carbohydrates and proteins per serving is requested
        Then percentages of fats, carbohydrates and proteins in each food item are calculated and their average values in all food items analysed.
        Returns a dictionary with 3 percentages (for fats, carbohydrates and proteins) and also containing all 'raw' data (food labels, products names, products IDs, fat/carb/prot percent) -
        see structure of 'main_output' dictionary
    '''
    print('###################### Foodlabel #######################')
    print('Foodlabel from dialogflow: ' + str(label_list))
    main_output = {}
    products_n = 1
    how_many_terms = 2
    for n in range(products_n):
        # Get IDs for items for each product
        # Request 'hits' (foods) list
        n1 = requests.get('https://api.nutritionix.com/v1_1/search/' + label_list[n] + '?results=0%3A' + str(how_many_terms) + '&cal_min=0&cal_max=50000&fields=item_name%2Cbrand_name%2Citem_id%2Cbrand_id&appId=' + nutrionix_app_id + '&appKey=' + nutrionix_app_key)
        ids = json.loads(n1.text)

        # Get foods id, name, [relevance] score
        #total_hits = ids['total_hits']
        hits = ids['hits']
        sub_output = []  # data for specific food item ID, [id, name, id_score, fats%, carbohydrates%, proteins%]
        for hit in hits:
            id = ''
            name = ''
            id_score = 0
            id = hit['fields']['item_id']
            name = hit['fields']['item_name']
            id_score = hit['_score']

            # For each food ID request nutrition data (fats, carbohydrates and proteins content in grams)
            n2 = requests.get('https://api.nutritionix.com/v1_1/item?id=' + str(id) + '&appId=' + nutrionix_app_id + '&appKey=' + nutrionix_app_key)
            nutr_data = json.loads(n2.text)

            fat_g, carbo_g, protein_g = 0, 0, 0
            fat_g = nutr_data['nf_total_fat']
            carbo_g = nutr_data['nf_total_carbohydrate']
            protein_g = nutr_data['nf_protein']

            # Calculate percentage content of fats, carbohydrates and proteins
            sum_g = fat_g + carbo_g + protein_g
            if sum_g == 0:
                sum_g = 1

            fat_perc, carbo_perc, protein_perc = 0, 0, 0
            fat_perc = fat_g * 100 / sum_g
            carbo_perc = carbo_g * 100 / sum_g
            protein_perc = protein_g * 100 / sum_g

            # Load data to list
            sub_output.append([id, name, id_score, fat_perc, carbo_perc, protein_perc])

        # Load lists of lists with data for each food item id into final dictionary with food terms
        main_output[label_list[n]] = sub_output

    # Calculate average nutrienst percent across all food items for all terms in our main_output dictionary (for eg., if we requested 3 terms [with 3 items for each one], then
    # average will be calculated for 3 * 3 = 9 values for each nutrient
    fat_sum, carbo_sum, prot_sum = 0, 0, 0
    for key, value in main_output.items():
        items_per_term = len(value)
        for item in value:
            fat_sum = fat_sum + item[3]
            carbo_sum = carbo_sum + item[4]
            prot_sum = prot_sum + item[5]

    divider = how_many_terms * products_n

    av_fat, av_carbo, av_prot = 0, 0, 0

    av_fat = fat_sum / divider
    av_carbo = carbo_sum / divider
    av_prot = prot_sum / divider

    main_output['average_percents'] = [round(av_fat, 2), round(av_carbo, 2), round(av_prot, 2)]
    print('###################### Main_output #######################')
    print(main_output)
    return(main_output)

def pygal_bar_chart(data, png_file_name, chart_name):
    bar_chart = pygal.Bar()             # Then create a bar graph object
    bar_chart.add(chart_name, data)     # Add some values
    bar_chart.render_to_png(png_file_name)
    return True

def split(txt, seps):
    # split input data by a list of possible separators
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [float(i.strip()) for i in txt.split()]

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

    # Check if the request is for the plotbot action
    elif action == 'plotbot':
        contexts = req.get('result').get('contexts')
        chart_data2split = contexts[0].get('parameters').get('chart-data.original')
        chart_data = split(chart_data2split, [' ', ',', ';', '-', '/'])

        pygal_bar_chart(chart_data,'test.png', 'test chart')

        print(req)
        print('************************')
        print(action)
        print('************************')
        print('chart_data: {}, type: {}.'.format(chart_data, type(chart_data)))

        # Compose the response to dialogflow.com
        res = {
            'speech': 'http://35.196.100.14/static/test.png',
            'displayText': 'http://35.196.100.14/static/test.png',
            'contextOut': req['result']['contexts']
            }

    else:
        # If the request is not of our actions throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    # Check if the request is for the action 'bar.chart-basic.style-webhook' - building a BASIC BAR chart
    elif action == 'bar.chart-basic.style-webhook':
        contexts = req.get('result').get('contexts')
        mychartdata = contexts[0].get('parameters')
        ds1, ds2, ds3 = '', '', '' # original string versions of our data strings (up to 5-10? can be added)
        ds1_err, ds2_err, ds3_err = False, False, False # error flags for data strings - we'll try to build a chart using at least 1 correct data string and inform user in case errors are found

        # data-series-X example: ["series A: 0, 1, 2, 3, 4", "5"]
        if 'data-series-1.original' in mychartdata:
            if mychartdata['data-series-1.original'][0] != '':
                ds1 = mychartdata['data-series-1.original'][0]
                # split this string by ':"
                # get ds name
                # get these hopefully numbers (string representation)
                # split them by possible delimiters
                # check if they are numbers and convert to float
            else:
                ds1_err = True
        else:
            ds1_err = True


        chart_data2split = contexts[0].get('parameters').get('chart-data.original')
        chart_data = split(chart_data2split, [' ', ',', ';', '-', '/'])

        pygal_bar_chart(chart_data,'test.png', 'test chart')

        print(req)
        print('************************')
        print(action)
        print('************************')
        print('chart_data: {}, type: {}.'.format(chart_data, type(chart_data)))

        # Compose the response to dialogflow.com
        res = {
            'speech': 'http://35.196.100.14/static/test.png',
            'displayText': 'http://35.196.100.14/static/test.png',
            'contextOut': req['result']['contexts']
            }

    else:
        # If the request is not of our actions throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }

    return make_response(jsonify(res))

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0')#, port=port)

'''
{
    "data":
        {
            "telegram":
                {
                    "reply_markup":
                        {
                            "inline_keyboard":
                                [
                                    [
                                        {
                                            "callback_data": "Red",
                                            "text": "Red"
                                        }
                                    ],
                                    [
                                        {
                                            "callback_data": "Green",
                                            "text": "Green"
                                        }
                                    ],
                                    [
                                        {
                                            "callback_data": "Yellow",
                                            "text": "Yellow"
                                        }
                                    ],
                                    [
                                        {
                                            "callback_data": "Blue",
                                            "text": "Blue"
                                        }
                                    ],
                                    [
                                        {
                                            "callback_data": "Pink",
                                            "text": "Pink"
                                        }
                                    ]
                                ]
                        },
                    "text": "Pick a color"
                }
        }
}

{
    'data':
        {
            'telegram':
                {
                    'photo': 'http://35.196.100.14/static/test.png'
                }
        }
}
'''
# JSON from webhook

{
  "id": "9770e9d4-e7ed-4ed1-8344-5c5ac7cd597f",
  "timestamp": "2018-02-06T09:26:11.25Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "yes",
    "action": "bar.chart-basic.style-webhook",
    "actionIncomplete": false,
    "parameters": {},
    "contexts": [
      {
        "name": "mychart",
        "parameters": {
          "data-series-1.original": [
            "series A: 0, 1, 2, 3, 4",
            "5"
          ],
          "bar-chart-styles": "basic",
          "data-series-1": [
            "series A 0 1 2 3 4",
            "5"
          ],
          "data-series-2": [
            "series Fibonacci 1 2 4 8 16 32"
          ],
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-2.original": "series Fibonacci: 1, 2, 4, 8, 16, 32",
          "data-series-0.original": "series A: 1, 2, 4, 5, 6, 7",
          "data-series-0": [
            "series A 1 2 4 5 6 7"
          ],
          "bar-chart-styles.original": "basic"
        },
        "lifespan": 5
      },
      {
        "name": "bar-basic-dataseries-add0-followup",
        "parameters": {
          "data-series-1.original": [
            "series A: 0, 1, 2, 3, 4",
            "5"
          ],
          "data-series-1": [
            "series A 0 1 2 3 4",
            "5"
          ],
          "data-series-2": [
            "series Fibonacci 1 2 4 8 16 32"
          ],
          "data-series-2.original": "series Fibonacci: 1, 2, 4, 8, 16, 32",
          "data-series-0.original": "series A: 1, 2, 4, 5, 6, 7",
          "data-series-0": [
            "series A 1 2 4 5 6 7"
          ]
        },
        "lifespan": 5
      },
      {
        "name": "bar-chart-basic-style",
        "parameters": {
          "data-series-1.original": [
            "series A: 0, 1, 2, 3, 4",
            "5"
          ],
          "bar-chart-styles": "basic",
          "data-series-1": [
            "series A 0 1 2 3 4",
            "5"
          ],
          "data-series-2": [
            "series Fibonacci 1 2 4 8 16 32"
          ],
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-2.original": "series Fibonacci: 1, 2, 4, 8, 16, 32",
          "data-series-0.original": "series A: 1, 2, 4, 5, 6, 7",
          "data-series-0": [
            "series A 1 2 4 5 6 7"
          ],
          "bar-chart-styles.original": "basic"
        },
        "lifespan": 1
      },
      {
        "name": "bar-basic-dataseries-add1-followup",
        "parameters": {
          "data-series-1.original": [
            "series A: 0, 1, 2, 3, 4",
            "5"
          ],
          "data-series-1": [
            "series A 0 1 2 3 4",
            "5"
          ],
          "data-series-2": [
            "series Fibonacci 1 2 4 8 16 32"
          ],
          "data-series-2.original": "series Fibonacci: 1, 2, 4, 8, 16, 32"
        },
        "lifespan": 4
      },
      {
        "name": "barchart-followup",
        "parameters": {
          "data-series-1.original": [
            "series A: 0, 1, 2, 3, 4",
            "5"
          ],
          "bar-chart-styles": "basic",
          "data-series-1": [
            "series A 0 1 2 3 4",
            "5"
          ],
          "data-series-2": [
            "series Fibonacci 1 2 4 8 16 32"
          ],
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-2.original": "series Fibonacci: 1, 2, 4, 8, 16, 32",
          "data-series-0.original": "series A: 1, 2, 4, 5, 6, 7",
          "data-series-0": [
            "series A 1 2 4 5 6 7"
          ],
          "bar-chart-styles.original": "basic"
        },
        "lifespan": 1
      }
    ],
    "metadata": {
      "intentId": "e97dff81-8705-47ec-8aa5-8dacb166ee0a",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 5001,
      "intentName": "bar.chart - basic.style - webhook"
    },
    "fulfillment": {
      "speech": "",
      "messages": [
        {
          "type": 0,
          "speech": ""
        }
      ]
    },
    "score": 1
  },
  "status": {
    "code": 206,
    "errorType": "partial_content",
    "errorDetails": "Webhook call failed. Error: Request timeout.",
    "webhookTimedOut": true
  },
  "sessionId": "55ae83c3-7561-4978-9b2e-a0e4282e1591"
}

