myinput = {
  "id": "bd671869-6201-460d-8986-7dc62cb3c85b",
  "timestamp": "2018-02-09T13:05:43.216Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "fibo: 1, 2, 4, 8",
    "action": "data-series-0",
    "actionIncomplete": False,
    "parameters": {
      "data-series-0": "fibo 1 2 4 8"
    },
    "contexts": [
      {
        "name": "mychart",
        "parameters": {
          "bar-chart-styles": "basic",
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-0.original": "1 2 4 8",
          "data-series-0": "fibo 1 2 4 8",
          "bar-chart-styles.original": "basic"
        },
        "lifespan": 5
      },
      {
        "name": "barchart-basicstyle-followup",
        "parameters": {
          "bar-chart-styles": "basic",
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-0.original": "fibo: 1, 2, 4, 8",
          "data-series-0": "fibo 1 2 4 8",
          "bar-chart-styles.original": "basic"
        },
        "lifespan": 5
      },
      {
        "name": "ready2plot",
        "parameters": {
          "data-series-0.original": "fibo: 1, 2, 4, 8",
          "data-series-0": "fibo 1 2 4 8"
        },
        "lifespan": 5
      }
    ],
    "metadata": {
      "intentId": "52ed7917-6920-4c68-b6e7-55ef6562d6ce",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 78,
      "intentName": "bar - basic - data.series - add0"
    },
    "fulfillment": {
      "speech": "Alright! Series 'fibo: 1, 2, 4, 8' for our basic bar chart received. Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh",
      "displayText": "Alright! Series 'fibo: 1, 2, 4, 8' for our basic bar chart received. Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh",
      "messages": [
        {
          "type": 0,
          "speech": "Alright! Series 'fibo: 1, 2, 4, 8' for our basic bar chart received. Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh"
        }
      ]
    },
    "score": 0.8999999761581421
  },
  "status": {
    "code": 200,
    "errorType": "success",
    "webhookTimedOut": False
  },
  "sessionId": "599970b1-d135-4ad5-a64d-941435705c53"
}

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
      ds_name = ds_splitted[0].strip() # any values including empty
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

def mysplit(txt, seps):
    # split input string by a list of possible separators, for eg. '4 - 4  5/ 5,6' >> ['4', '4', '5', '5', '6']
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split()]

contexts = myinput.get('result').get('contexts')
mychartdata = contexts[0].get('parameters')

print(get_data(mychartdata, 'data-series-0.original'))