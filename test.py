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

myjson = {
  "id": "0ec519b1-c3bb-4acb-91eb-b9e97b1d795a",
  "timestamp": "2018-02-11T21:16:06.278Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "2 3 4",
    "action": "data-series-0",
    "actionIncomplete": False,
    "parameters": {
      "data-series-0": "2 3 4"
    },
    "contexts": [
      {
        "name": "mychart",
        "parameters": {
          "bar-chart-styles": "basic",
          "chartname": "sdf",
          "validated_ds":
            {
              "1": 2,
              "2": 30
            }
          ,
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-0.original": "2 3 4",
          "data-series-0": "2 3 4",
          "chartname.original": "sdf",
          "bar-chart-styles.original": "horizontal"
        },
        "lifespan": 5
      },
      {
        "name": "barchart-basicstyle-followup",
        "parameters": {
          "bar-chart-styles": "horizontal",
          "chart-types": "bar chart",
          "chart-types.original": "",
          "data-series-0.original": "2 3 4",
          "data-series-0": "2 3 4",
          "bar-chart-styles.original": "horizontal"
        },
        "lifespan": 5
      },
      {
        "name": "ready2plot",
        "parameters": {
          "data-series-0.original": "2 3 4",
          "data-series-0": "2 3 4"
        },
        "lifespan": 5
      }
    ],
    "metadata": {
      "intentId": "52ed7917-6920-4c68-b6e7-55ef6562d6ce",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 77,
      "intentName": "bar.chart - all.styles - add.data"
    },
    "fulfillment": {
      "speech": "Alright! Series \"\": [2.0, 3.0, 4.0] for our horizontal bar chart entitled 'sdf' received (in addition to series \"\": [2.0, 3.0, 4.0, 5.0]). Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh",
      "displayText": "Alright! Series \"\": [2.0, 3.0, 4.0] for our horizontal bar chart entitled 'sdf' received (in addition to series \"\": [2.0, 3.0, 4.0, 5.0]). Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh",
      "messages": [
        {
          "type": 0,
          "speech": "Alright! Series \"\": [2.0, 3.0, 4.0] for our horizontal bar chart entitled 'sdf' received (in addition to series \"\": [2.0, 3.0, 4.0, 5.0]). Please add another data series or may I draw our chart? If something is wrong please write 'restart' to start afresh"
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

contexts = myjson.get('result').get('contexts')
for context in contexts:
    if context['name'] == 'mychart':
        charttype = context['parameters']['chart-types']
        chartsubtype = context['parameters']['bar-chart-styles']
        data2plot = context['parameters'][
            'validated_ds']  # is a list for eg. [{"fibo": [1, 2, 4, 8]}, {"next": [2, 3, 4, 5]}]
        chartname = context['parameters']['chartname']

# to name our chart we'll use last 12 digist of 'id' from JSON got from dialogflow
ourfilename = 'static/' + myjson.get('id')[-12:]
print('charttype - ' + charttype)
print('chartsubtype - ' + chartsubtype)
print('data2plot - ' + str(data2plot))
print('chartname - ' + chartname)

if chartsubtype == 'basic':
    print('basic!')
    pygal_pie_basic(data2plot, chartname, ourfilename)
elif chartsubtype == 'horizontal':
    print('horizontal!')
    pygal_pie_donut(data2plot, chartname, ourfilename)
elif chartsubtype == 'stacked':
    print('stacked!')
    pygal_pie_halfpie(data2plot, chartname, ourfilename)