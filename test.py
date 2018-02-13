import os
import json
from flask import Flask, request, make_response, jsonify
import pygal
from pygal.style import DefaultStyle
import cairosvg

# Bar chart - basic
def pygal_bar_basic(data, chartname, file_name):
    bar_chart = pygal.Bar()
    bar_chart = pygal.Bar(print_values=True, style=DefaultStyle(
        value_font_family='googlefont:Raleway',
        value_font_size=30,
        value_colors=('white',)))
    bar_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            bar_chart.add(key, value)
    bar_chart.render_to_file(file_name + '.svg')
    bar_chart.render_to_png(file_name + '.png')
    return True

# Bar chart - horizontal
def pygal_bar_horizontal(data, chartname, file_name):
    print('here!')
    bar_chart1 = pygal.HorizontalBar()
    bar_chart1 = pygal.HorizontalBar(print_values=True, style=DefaultStyle(
        value_font_family='googlefont:Raleway',
        value_font_size=30,
        value_colors=('white',)))
    bar_chart1.title = chartname
    for ds in data:
        for key, value in ds.items():
            bar_chart1.add(key, value)
    bar_chart1.render_to_file(file_name + '.svg')
    bar_chart1.render_to_png(file_name + '.png')
    return True

# Bar chart - stacked
def pygal_bar_stacked(data, chartname, file_name):
    bar_chart2 = pygal.StackedBar()
    bar_chart2 = pygal.StackedBar(print_values=True, style=DefaultStyle(
        value_font_family='googlefont:Raleway',
        value_font_size=30,
        value_colors=('white',)))
    bar_chart2.title = chartname
    for ds in data:
        for key, value in ds.items():
            bar_chart2.add(key, value)
    bar_chart2.render_to_file(file_name + '.svg')
    bar_chart2.render_to_png(file_name + '.png')
    return True

# Line chart - basic
def pygal_line_basic(data, chartname, file_name):
    line_chart = pygal.Line(print_values=True)
    line_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            line_chart.add(key, value)
    line_chart.render_to_file(file_name + '.svg')
    line_chart.render_to_png(file_name + '.png')
    return True

# Line chart - horizontal
def pygal_line_horizontal(data, chartname, file_name):
    line_chart = pygal.HorizontalLine(print_values=True)
    line_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            line_chart.add(key, value)
    line_chart.render_to_file(file_name + '.svg')
    line_chart.render_to_png(file_name + '.png')
    return True

# Line chart - stacked
def pygal_line_stacked(data, chartname, file_name):
    line_chart = pygal.StackedLine(print_values=True)
    line_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            line_chart.add(key, value)
    line_chart.render_to_file(file_name + '.svg')
    line_chart.render_to_png(file_name + '.png')
    return True

# Pie chart - basic
def pygal_pie_basic(data, chartname, file_name):
    pie_chart = pygal.Pie()
    pie_chart.title = chartname
    for key, value in data.items():
        pie_chart.add(key, value)
    pie_chart.render_to_file(file_name + '.svg')
    pie_chart.render_to_png(file_name + '.png')
    return True

# Pie chart - donut
def pygal_pie_donut(data, chartname, file_name):
    pie_chart = pygal.Pie(inner_radius=.4)
    pie_chart.title = chartname
    for key, value in data.items():
        pie_chart.add(key, value)
    pie_chart.render_to_file(file_name + '.svg')
    pie_chart.render_to_png(file_name + '.png')
    return True

# Pie chart - half pie
def pygal_pie_halfpie(data, chartname, file_name):
    pie_chart = pygal.Pie(half_pie=True)
    pie_chart.title = chartname
    for key, value in data.items():
        pie_chart.add(key, value)
    pie_chart.render_to_file(file_name + '.svg')
    pie_chart.render_to_png(file_name + '.png')
    return True

def get_pie_data(mychartdata, ds_key):
    # Function is used to parse and validate data series for pie charts
    # Function takes the name of data series (for eg., 'data-series-1.original') and json from webhook
    # ('result' >> 'contexts'['mychart'] >> 'parameters') and returns a dictionary containing
    # a name of this data series and corresponding number in format {'data-series-1.original_name': 'B', 'data-series-1.original_data': 2.0]}
    # in case of invalid input (no numbers) - returns error flag
    ds_data = 0
    ds_name = ''
    result_code = 'ok'
    ds = mychartdata[ds_key]
    if ds == '':
        output = [
            'bad',
            "Eh. Invalid data series. Please enter correct data in format 'series name (optionally): one number', for eg. 'Product 1: 63' or just '63'",
            {}
            ]
        return output

    # user is supposed to have entered smth like 'series C: 4' or just '4' (both ok)
    # but he/she may have entered invalid (non-digit) values  like 'sdsdfsd sddd' or ',, ,,, ,'
    # or semi-correct data, for eg. with several data series like 'A: 3, B: 3, C: 4' (at this stage he is supposed to enter data series one at a time)

    # try to split this string by ':"
    # possible results:
    # 1. input doesn't contain ':' - we'll get a list with 1 value to validate as a 1 number // '4' , '4, 5, 5', ' ', 'sdfsdfsdf sdsdds'
    # 1.1 also user may have forgotten to enter ':' in a valid input, for eg. 'series C 4' or 'series-500 4' - for now this variant will be considered invalid but later
    # some logics may be added to recognise it as valid
    # 2. input contains 1 ':' - we'll get a list with 2 values, the 1st - ds name, the 2nd - ds data // 'series C: 4', 'sdfsdf: sddd', ':'
    # 3. input contains >1 ':' - we'll get a list with >2 values, the 1st will be ds name, the 2nd - ds data, all the rest will be discarded // 'series C: 4, series D: 1, 2, 3, 5,3'
    ds_splitted = ds.split(':')
    if len(ds_splitted) == 1:
        ds_data_part = mysplit(ds_splitted[0].strip(), [' ', ' . ', ',', ';', '- ', '/'])
    else:
        ds_name = ds_splitted[0].strip() # any values including empty
        ds_data_part = mysplit(ds_splitted[1].strip(), [' ', ' . ', ',', ';', '- ', '/'])

    # so we have a part ds_data_part which is supposed to be a number. variants:
    # 1. correct data ('4') - result code 'ok'
    # 2. completely incorrect data ('', 'sdsdd', '4.sd') - result code 'bad'
    # 3. partly correct data ('2.3, 2.0', '2.3, sdsd') - results code 'partly'
    # we'll try to convert these data to float numbers, all nondigit values will be substituted with 0
    # in case all series contains only 0s (valid 0s or nondigit values substituted with 0) - result code 'bad'
    # series theoretically can be =0
    if len(ds_data_part) > 1:
        result_code = 'partly'

    try:
        ds_data = float(ds_data_part[0])
    except ValueError:
        ds_data = 0
        result_code = 'bad'

    # so now we have variants with result codes:
    # 1. 'ok' = a valid number with or without ds name
    # 2. 'partly' = a valid number with or without ds name but user entered >1 value for one ds
    # 3. 'bad' = empty (after deleting delimiters) or non-numeric value
    # p.s. some additional data for response compilation - chart type and subtype
    # We'll return [result_code][message][validated_data_series as dictionary {ds_name: ds_data}]
    chart_type = mychartdata['chart-types']
    chart_subtype = '[undefined]'
    if 'pie-chart-styles' in mychartdata:
        chart_subtype = mychartdata['pie-chart-styles']
    chart_name = mychartdata['chartname']

    # we also need to check for previous validated series to display them to user
    if 'validated_ds' in mychartdata:
        already_validated_data = mychartdata['validated_ds'] # is a dictionary with a dictionary as value {"validated_ds": {"ser1": 1, "": 9}}
        already_validated_data_nice = ' (in addition to series '
        x = 0
        for key, value in already_validated_data.items():
            if x>0:
                already_validated_data_nice += ', '
            already_validated_data_nice += '"{}": {}'.format(key, value)
        already_validated_data_nice += '). '
    else:
        already_validated_data_nice = '. '

    if result_code == 'ok':
        output = [
            'ok',
            'Alright! Series "' + ds_name + '": ' + str(ds_data) + " for our " + chart_subtype + " " + chart_type + " entitled '" + chart_name + "' received" + already_validated_data_nice + "Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh",
            {ds_name: ds_data}
        ]
    elif result_code == 'partly':
        output = [
            'partly',
            "Some errors were found in your data (maybe >1 values for data series). After correction we will get '" + ds_name + ": " + str(ds_data) + already_validated_data_nice + "Start afresh (write 'restart'), add another data series (please follow the same format, 'Series1: 55.2') or draw a chart?",
            {ds_name: ds_data}
            ]
    else:
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'series name (optionally): one number', for eg. 'Product 1: 63' or just '63'",
            {}
            ]

    return output



myjson = {
  "id": "0b7f869a-fbb6-404a-a300-9bca46560cf5",
  "timestamp": "2018-02-13T10:28:42.379Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "sdfsdf: 233",
    "action": "data-series-pie",
    "actionIncomplete": False,
    "parameters": {
      "data-series-0": "sdfsdf"
    },
    "contexts": [
      {
        "name": "piechart-basicstyle-followup",
        "parameters": {
          "pie-chart-styles": "basic",
          "chart-types": "pie chart",
          "chart-types.original": "",
          "pie-chart-styles.original": "basic",
          "data-series-0.original": "sdfsdf",
          "data-series-0": "sdfsdf"
        },
        "lifespan": 2
      },
      {
        "name": "mychart",
        "parameters": {
          "chartname": "sdfsdf",
          "pie-chart-styles": "basic",
          "chart-types": "pie chart",
          "pie-chart-styles.original": "basic",
          "chart-types.original": "",
          "data-series-0.original": "sdfsdf",
          "data-series-0": "sdfsdf",
          "chartname.original": "sdfsdf"
        },
        "lifespan": 5
      }
    ],
    "metadata": {
      "intentId": "91c8fc49-c520-4842-a597-7248e0904fc1",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 78,
      "intentName": "pie.chart - all.styles - add.data"
    },
    "fulfillment": {
      "speech": "Invalid data series. Please enter correct data in format 'series name (optionally): one number', for eg. 'Product 1: 63' or just '63'",
      "displayText": "Invalid data series. Please enter correct data in format 'series name (optionally): one number', for eg. 'Product 1: 63' or just '63'",
      "messages": [
        {
          "type": 0,
          "speech": "Invalid data series. Please enter correct data in format 'series name (optionally): one number', for eg. 'Product 1: 63' or just '63'"
        }
      ]
    },
    "score": 0.8700000047683716
  },
  "status": {
    "code": 200,
    "errorType": "success",
    "webhookTimedOut": False
  },
  "sessionId": "599970b1-d135-4ad5-a64d-941435705c53"
}

mypie = {
  "id": "7fdd226b-f5a6-48f1-bcbb-8094000191d4",
  "timestamp": "2018-02-13T10:19:32.715Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "6565",
    "action": "data-series-pie",
    "actionIncomplete": False,
    "parameters": {
      "data-series-0": "6565"
    },
    "contexts": [
      {
        "name": "piechart-basicstyle-followup",
        "parameters": {
          "pie-chart-styles": "basic",
          "chart-types": "pie chart",
          "chart-types.original": "",
          "pie-chart-styles.original": "usual",
          "data-series-0.original": "6565",
          "data-series-0": "6565"
        },
        "lifespan": 2
      },
      {
        "name": "mychart",
        "parameters": {
          "chartname": "sdfsdf",
          "pie-chart-styles": "basic",
          "chart-types": "pie chart",
          "validated_ds": {
            "wanne": 5050
          },
          "pie-chart-styles.original": "usual",
          "chart-types.original": "",
          "data-series-0.original": "sees: 6565",
          "data-series-0": "6565",
          "chartname.original": "sdfsdf"
        },
        "lifespan": 5
      },
      {
        "name": "ready2plot",
        "parameters": {
          "data-series-0.original": "6565",
          "data-series-0": "6565"
        },
        "lifespan": 5
      }
    ],
    "metadata": {
      "intentId": "91c8fc49-c520-4842-a597-7248e0904fc1",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 77,
      "intentName": "pie.chart - all.styles - add.data"
    },
    "fulfillment": {
      "speech": "Alright! Series \"\": 6565.0 for our basic pie chart entitled 'sdfsdf' received. Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh",
      "displayText": "Alright! Series \"\": 6565.0 for our basic pie chart entitled 'sdfsdf' received. Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh",
      "messages": [
        {
          "type": 0,
          "speech": "Alright! Series \"\": 6565.0 for our basic pie chart entitled 'sdfsdf' received. Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh"
        }
      ]
    },
    "score": 1
  },
  "status": {
    "code": 200,
    "errorType": "success",
    "webhookTimedOut": False
  },
  "sessionId": "599970b1-d135-4ad5-a64d-941435705c53"
}

def mysplit(txt, seps):
    # split input string by a list of possible separators, for eg. '4 - 4  5/ 5,6' >> ['4', '4', '5', '5', '6']
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split()]

extract = mypie['result']['contexts']
for context in extract:
    if context['name'] == 'mychart':
        mychartdata = context['parameters']

print(get_pie_data(mychartdata, 'data-series-0.original'))
