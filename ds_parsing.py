import json

def mysplit(txt, seps):
    # split input data by a list of possible separators
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split()]

def get_data(mychartdata, ds_key):
    # take key of data series (for eg., 'data-series-1.original') and return a dictionary {'key_name': <key_ds_name>, 'key_data': <key_ds_data>}
    ds_data = []
    ds_name = ''
    if ds_key == 'data-series-1.original':
        ds = mychartdata[ds_key][0]
    else:
        ds = mychartdata[ds_key]
    print('***************** ds-' + ds_key + ' ******************')
    print(ds)

    # split this string by ':"
    ds_splitted = ds.split(':')
    # get ds name. It may be empty, may or may not contain keyword 'series'
    ds_name_part = ds_splitted[0].strip()

    if 'series' in ds_name_part.lower():
        ds_name = ds_name_part[ds_name_part.lower().find('series') + 6:].strip()
        print('***************** ds_name-' + ds_key + ' ******************')
        print(ds_name)

    # get these hopefully numbers (string representation)
    # split them by possible delimiters
    ds_data_part = mysplit(ds_splitted[1].strip(), [' ', ',', ';', '-', '/'])

    # check if they are numbers and convert to float
    # all non-numbers will be substituted with 0
    for item in ds_data_part:
        if item.isdigit():
            ds_data.append(float(item))
        else:
            ds_data.append(0)

    print('***************** ds-' + ds_key + ' name, data ******************')
    print(ds_name_part)
    print(ds_data_part)

    print('***************** ds1_data ******************')
    print(ds_data)

    output = {ds_key+'_name': ds_name, ds_key+'_data': ds_data}
    return output

def get_ds(req):
    contexts = req.get('result').get('contexts')
    print('***************** CONTEXTS ******************')
    print(contexts)

    mychartdata = contexts[0].get('parameters')
    print('***************** mychartdata ******************')
    print(mychartdata)

    ds0, ds1, ds2 = {}, {}, {}  # containers for our data strings
    ds1_err, ds2_err, ds3_err = False, False, False  # error flags for data strings - we'll try to build a chart using at least 1 correct data string and inform user in case errors are found

    # data-series-X example: ["series A: 0, 1, 2, 3, 4", "5"]
    if 'data-series-0.original' in mychartdata and mychartdata['data-series-0.original'] != '':
            ds0 = get_data(mychartdata, 'data-series-0.original')
    else:
        ds0_err = True

    if 'data-series-1.original' in mychartdata and mychartdata['data-series-1.original'][0] != '':
            ds1 = get_data(mychartdata, 'data-series-1.original')
    else:
        ds1_err = True

    if 'data-series-2.original' in mychartdata and mychartdata['data-series-2.original'] != '':
            ds2 = get_data(mychartdata, 'data-series-2.original')
    else:
        ds2_err = True

    print('****************************** RESULTS *****************************')
    print(ds0)
    print(ds1)
    print(ds2)
    return True

ourjson = {
  "id": "9770e9d4-e7ed-4ed1-8344-5c5ac7cd597f",
  "timestamp": "2018-02-06T09:26:11.25Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "yes",
    "action": "bar.chart-basic.style-webhook",
    "actionIncomplete": False,
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
    "webhookTimedOut": True
  },
  "sessionId": "55ae83c3-7561-4978-9b2e-a0e4282e1591"
}

print(get_ds(ourjson))