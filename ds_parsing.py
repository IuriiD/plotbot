import json

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
    ds_name = ' '
    invalidinput = False
    ds = mychartdata[ds_key]

    # user is supposed to have entered smth like 'series C: 4, 4, 5, 5,6' or 'C: 4, 4, 5, 5,6' or at least '4, 4, 5, 5,6' - all ok
    # but he/she may have entered invalid (non-digit) values  like 'sdsdfsd sddd' or ',, ,,, ,'

    # split this string by ':"
    # in case of several ':' in this string only data to the left and to the right of the 1st ':' will be taken
    ds_splitted = ds.split(':')
    # get ds name. It may be empty, may or may not contain keyword 'series'
    ds_name_part = ds_splitted[0].strip()

    if 'series' in ds_name_part.lower():
        ds_name = ds_name_part[ds_name_part.lower().find('series') + 6:].strip()
    else:
        ds_name = ds_name_part

    # get these hopefully numbers (string representation)
    # split them by possible delimiters
    ds_data_part = mysplit(ds_splitted[1].strip(), [' ', ',', ';', '-', '/'])

    # at this stage in case of invalid input we may get empty string (for smth like ',, ,,, ,' after all delimiters were stripped)
    # or string with nondigit characters
    if ds_data_part == '':
        invalidinput = True

    # check if they are numbers and convert to float
    # all non-numbers will be substituted with 0
    for item in ds_data_part:
        if item.isdigit():
            ds_data.append(float(item))
        else:
            ds_data.append(0)

    # compile output
    output = {ds_key+'_name': ds_name, ds_key+'_data': ds_data}
    return output

def get_ds(req):
    # function takes JSON, received from dialogflow, and returns data series ready to build charts
    #  get 'contexts'
    contexts = req.get('result').get('contexts')

    # from the 1st context (supposed to be 'mychart') get 'parameters'
    mychartdata = contexts[0].get('parameters')

    # set default values
    ds0, ds1, ds2 = {}, {}, {}  # containers for our data series

    # data-series-X example: ["series A: 0, 1, 2, 3, 4", "5"]
    # at this stage there may be from 1 to 3 data series (data-series-0, data-series-1 and data-series-2)
    # possible variants:
    # a) all DS entered by user are Ok - draw and return a chart - 'errors': 'no'
    # b) at least 1 DS is ok but another/other is/are invalid - draw chart but inform about errors - 'errors': 'some'
    # c) all entered DS are invalid - no chart, inform user about errors - 'errors': 'all'
    output = {'data': [], 'errors' = 'all'} # output dictionary,for eg.
    '''
    {
        'data':
            [
                {'A': [1.0, 2.0, 3.0, 4.0, 5.0]},
                {'B': [2.0, 4.0, 5.0, 6.0, 6.0]},
                {'C': [4.0, 4.0, 5.0, 5.0, 6.0]}
        ],
        'errors': 'no'
    }
    '''

    if 'data-series-0.original' in mychartdata:
        if mychartdata['data-series-0.original'] != '':
            ds0 = get_data(mychartdata, 'data-series-0.original')
            print(ds0)
            output['data'].append({ds0['data-series-0.original_name']:ds0['data-series-0.original_data']})
            output['errors'] = 'no'
        else:
            output['errors'] = 'all'

    if 'data-series-1.original' in mychartdata:
        if mychartdata['data-series-1.original'][0] != '':
            ds1 = get_data(mychartdata, 'data-series-1.original')
            print(ds1)
            output['data'].append({ds1['data-series-1.original_name']:ds1['data-series-1.original_data']})
            if output['errors'] == 'all':
                output['errors'] = 'some'
        else:
            output['errors'] = 'all'

    if 'data-series-2.original' in mychartdata:
        if mychartdata['data-series-2.original'] != '':
            ds2 = get_data(mychartdata, 'data-series-2.original')
            print(ds2)
            output[ds2['data-series-2.original_name']] = ds2['data-series-2.original_data']
            if output['errors'] == 'all':
                output['errors'] = 'some'
        else:
            ds2_err = True

    print(output)
    return output

ourjson = {
        "id": "7bcbc87a-f0d2-40b4-8a3c-5de0febe4886",
        "timestamp": "2018-02-07T09:12:45.199Z",
        "lang": "en",
        "result": {
            "source": "agent",
            "resolvedQuery": "draw chart",
            "action": "bar.chart-basic.style-webhook",
            "actionIncomplete": False,
            "parameters": {},
            "contexts": [
                {
                    "name": "mychart",
                    "parameters": {
                        "data-series-1.original": "series B: 2, 4, 5, 6, 6",
                        "bar-chart-styles": "basic",
                        "data-series-1": [
                            "series B 2 4 5 6 6"
                        ],
                        "data-series-2": [
                            "series C 4 4 5 5,6"
                        ],
                        "chart-types": "bar chart",
                        "chart-types.original": "",
                        "data-series-2.original": "series C: 4, 4, 5, 5,6",
                        "data-series-0.original": "series A: 1, 2, 3, 4, 5",
                        "data-series-0": [
                            "series A 1 2 3 4 5"
                        ],
                        "bar-chart-styles.original": "basic"
                    },
                    "lifespan": 5
                },
                {
                    "name": "ready2plot",
                    "parameters": {
                        "data-series-1.original": "series B: 2, 4, 5, 6, 6",
                        "data-series-1": [
                            "series B 2 4 5 6 6"
                        ],
                        "data-series-2": [
                            "series C 4 4 5 5,6"
                        ],
                        "data-series-2.original": "series C: 4, 4, 5, 5,6",
                        "data-series-0.original": "series A: 1, 2, 3, 4, 5",
                        "data-series-0": [
                            "series A 1 2 3 4 5"
                        ]
                    },
                    "lifespan": 5
                }
            ],
            "metadata": {
                "intentId": "49da9c59-c872-4aff-adf2-3ed1e6fbfeb5",
                "webhookUsed": "false",
                "webhookForSlotFillingUsed": "false",
                "intentName": "bar.chart-basic.style-webhook"
            },
            "fulfillment": {
                "speech": "Ok. Let's sum up: we are building basic bar chart for series A: 1, 2, 3, 4, 5, series B: 2, 4, 5, 6, 6, series C: 4, 4, 5, 5,6. Right?",
                "messages": [
                    {
                        "type": 0,
                        "platform": "telegram",
                        "speech": "Ok. Let's sum up: we are building basic bar chart for series A: 1, 2, 3, 4, 5, series B: 2, 4, 5, 6, 6. Right?"
                    },
                    {
                        "type": 0,
                        "speech": "Ok. Let's sum up: we are building basic bar chart for series A: 1, 2, 3, 4, 5, series B: 2, 4, 5, 6, 6, series C: 4, 4, 5, 5,6. Right?"
                    }
                ]
            },
            "score": 0.7550243233925923
        },
        "status": {
            "code": 200,
            "errorType": "success",
            "webhookTimedOut": False
        },
        "sessionId": "55ae83c3-7561-4978-9b2e-a0e4282e1591"
    }

print(get_ds(ourjson))