# this is the version working at 'chatbots' VM in GC

import os
import re
import json
import requests
from flask import Flask, request, make_response, jsonify
from keys import nutrionix_app_id, nutrionix_app_key
import pygal
from pygal.style import DefaultStyle
import cairosvg

app = Flask(__name__)

# ###################### Food Composition Chatbot Functions ##############################

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
# ###################### Food Composition Chatbot Functions END ##############################

# ###################### Plotbot Functions ##############################

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
    bar_chart = pygal.HorizontalBar()
    bar_chart = pygal.HorizontalBar(print_values=True, style=DefaultStyle(
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

# Bar chart - stacked
def pygal_bar_stacked(data, chartname, file_name):
    bar_chart = pygal.StackedBar()
    bar_chart = pygal.StackedBar(print_values=True, style=DefaultStyle(
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
    line_chart = pygal.StackedLine(fill=True)
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
    for ds in data:
        for key, value in ds.items():
            pie_chart.add(key, value)
    pie_chart.render_to_file(file_name + '.svg')
    pie_chart.render_to_png(file_name + '.png')
    return True

# Pie chart - donut
def pygal_pie_donut(data, chartname, file_name):
    pie_chart = pygal.Pie(inner_radius=.4)
    pie_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            pie_chart.add(key, value)
    pie_chart.render_to_file(file_name + '.svg')
    pie_chart.render_to_png(file_name + '.png')
    return True

# Pie chart - half pie
def pygal_pie_halfpie(data, chartname, file_name):
    pie_chart = pygal.Pie(half_pie=True)
    pie_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            pie_chart.add(key, value)
    pie_chart.render_to_file(file_name + '.svg')
    pie_chart.render_to_png(file_name + '.png')
    return True

# Scatter chart
def pygal_scatter(data, chartname, file_name):
    xy_chart = pygal.XY(stroke=False)
    xy_chart.title = chartname
    for ds in data:
        for key, value in ds.items():
            xy_chart.add(key, value)
    xy_chart.render_to_file(file_name + '.svg')
    xy_chart.render_to_png(file_name + '.png')
    return True

def mysplit(txt, seps):
    # split input string by a list of possible separators, for eg. '4 - 4  5/ 5,6' >> ['4', '4', '5', '5', '6']
    default_sep = seps[0]
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split()]

def scatter_data_parse(ds_splitted):
    # Function takes what is supposed to be the numeric part of data series for scatter plot (a list of strings,
    # for eg. '(1, 2), (3, 4)') and returns a list of lists, each containing pairs of strings that will be further
    # validated as numbers
    # 1. Replace possible [] or {} brackets with ()
    ds_data_part = []
    ds_data_str = ds_splitted.replace('[', '(')
    ds_data_str = ds_data_str.replace(']', ')')
    ds_data_str = ds_data_str.replace('{', '(')
    ds_data_str = ds_data_str.replace('}', ')')
    print('ds_data_str: ', str(ds_data_str))

    # 2. Now check if there are '(' in our string; there's one possible correct variant without '()": with only 1 tuple (2 numbers)
    if not '(' in ds_data_str:
        # take the first 2 values (supposed to be numbers)
        ds_data_part.append(mysplit(ds_data_str.strip(), [' ', ' . ', ',', ';', '- ', '/'])[:2])
        print('Here0')
    else:
        # split our string by blocks in "(...)" brackets
        ds_data_strtuples = re.findall("\((.*?)\)", ds_data_str)
        for pair in ds_data_strtuples:
            ds_data_part.append(mysplit(pair.strip(), [' ', ' . ', ',', ';', '- ', '/']))
    return(ds_data_part)

def get_bar_line_data(mychartdata, ds_key):
    # Function is used to parse and validate data series for bar and line charts
    # Function takes the name of data series (for eg., 'data-series-1.original') and json from webhook
    # ('result' >> 'contexts'['mychart'] >> 'parameters') and returns a dictionary containing
    # a name of this data series and corresponding numbers in format {'data-series-1.original_name': 'B', 'data-series-1.original_data': [2.0, 4.0, 5.0, 6.0, 6.0]}
    # in case of invalid input (no numbers) - returns error flag
    ds_data = []
    ds_name = ''
    result_code = 'ok'
    ds = mychartdata[ds_key]
    if ds == '':
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'Series name (optionally): series data', for eg. 'Fibonacci: 1, 2, 4, 8, 16, 32'",
            {}
            ]
        return output

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
        ds_data_part = mysplit(ds_splitted[0].strip(), [' ', ' . ', ',', ';', '- ', '/'])
    else:
        ds_name = ds_splitted[0].strip() # any values including empty
        ds_data_part = mysplit(ds_splitted[1].strip(), [' ', ' . ', ',', ';', '- ', '/'])

    # so we have a part supposed to be data series. variants:
    # 1. correct data ('4', '4', '5', '5', '6') - result code 'ok'
    # 2. completely incorrect data (''; 'sdsdd', 'sds') - result code 'bad'
    # 3. partly correct data ('sdfs', '4.0', '2.3', 'ssdsd') - results code 'partly'
    # we'll try to convert these data to float numbers, all nondigit values will be substituted with 0
    # in case all series contains only 0s (valid 0s or nondigit values substituted with 0) - result code 'bad'
    for item in ds_data_part:
        try:
            ds_data.append(float(item))
        except ValueError:
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
    if 'bar-chart-styles' in mychartdata:
        chart_subtype = mychartdata['bar-chart-styles']
    elif 'line-chart-styles' in mychartdata:
        chart_subtype = mychartdata['line-chart-styles']
    chart_name = mychartdata['chartname']

    # we also need to check for previous validated series to display them to user
    if 'validated_ds' in mychartdata:
        already_validated_data = mychartdata['validated_ds'] # is a list of dictionaries "validated_ds": [{"": [1, 2, 3]}, {"": [0, 9, 3]}]
        already_validated_data_nice = ' (in addition to series '
        for x in range(len(already_validated_data)):
            for key, value in already_validated_data[x].items():
                if x>0:
                    already_validated_data_nice += ', '
                already_validated_data_nice += '"{}": {}'.format(key, value)
        already_validated_data_nice += '). '
    else:
        already_validated_data_nice = '. '

    if result_code == 'ok':
        output = [
            'ok',
            'Alright! Series "' + ds_name + '": ' + str(ds_data) + " for our " + chart_subtype + " " + chart_type + " entitled '" + chart_name + "' received" + already_validated_data_nice,
            {ds_name: ds_data}
        ]
    elif result_code == 'partly':
        output = [
            'partly',
            "Some errors were found in your data. After replacing those errors with 0, we will get '" + ds_name + ": " + str(ds_data) + already_validated_data_nice,
            {ds_name: ds_data}
            ]
    else:
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'series name (optionally): series data', for eg. 'Fibonacci: 1, 2, 4, 8, 16, 32' or '10 20 30'",
            {}
            ]

    return output

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
        already_validated_data = mychartdata['validated_ds'] # is a list of dictionaries "validated_ds": [{"": 1 }, {"": 9}]
        already_validated_data_nice = ' (in addition to series '
        for x in range(len(already_validated_data)):
            for key, value in already_validated_data[x].items():
                if x>0:
                    already_validated_data_nice += ', '
                already_validated_data_nice += '"{}": {}'.format(key, value)
        already_validated_data_nice += '). '
    else:
        already_validated_data_nice = '. '


    if result_code == 'ok':
        output = [
            'ok',
            'Alright! Series "' + ds_name + '": ' + str(ds_data) + " for our " + chart_subtype + " " + chart_type + " entitled '" + chart_name + "' received" + already_validated_data_nice,
            {ds_name: ds_data}
        ]
    elif result_code == 'partly':
        output = [
            'partly',
            "Some errors were found in your data (maybe >1 values for data series). After correction we will get '" + ds_name + ": " + str(ds_data) + already_validated_data_nice,
            {ds_name: ds_data}
            ]
    else:
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'series name (optionally): one number', for eg. 'Product 1: 63' or just '63'",
            {}
            ]

    return output

def get_scatter_data(mychartdata, ds_key):
    # Function is used to parse and validate data series for scatter plots
    # Function takes the name of data series (for eg., 'data-series-1.original') and json from webhook
    # ('result' >> 'contexts'['mychart'] >> 'parameters') and returns a dictionary containing
    # a name of this data series and corresponding numbers in format {'data-series-1.original_name': 'B', 'data-series-1.original_data': (2.0, 3.0), (2.5, 5.2), (2.9, 10.0)]}
    # so for a scatter plot user is supposed to have entered at least 1 tuple of numbers (2 numbers in round brackets) (optionally also a data series name at the beginning separated with ':')
    # [] or {} brackets are also allowed
    # in case of invalid input (no numbers) - returns error flag
    ds_data = []
    ds_name = ''
    result_code = 'ok'
    ds = mychartdata[ds_key]
    if ds == '':
        output = [
            'bad',
            "Eh. Invalid input. Please enter your data series (one at a time) in format 'series name (optionally): series data', for eg. 'TheBigOnes: (1, 2), (2, 4), (3, 5)' or just '(1, 2), (2, 4), (3, 5)",
            {}
            ]
        return output

    # user is supposed to have entered smth like 'series C: (2, 3), (2, 5), (2, 10)' or just '(2, 3), (2, 5), (2, 10)' (both ok; brackets may be (), [], {}; any delimiters between numbers and tuples may be used)
    # but he/she may have entered invalid (non-digit) values  like 'sdsdfsd sddd' or ',, ,,, ,'
    # or semi-correct data, for eg. with several data series like 'A: (2, 3), B: (4, 6), C: (10, 30)' (at this stage he is supposed to enter data series one at a time)

    # try to split this string by ':"
    # possible results:
    # 1. input doesn't contain ':' - we'll get a list with 1 value to validate as a 1 number // '4, 5' , '(4 5)', '(2, 3), (2, 5), (2, 10)', ' ', 'sdfsdfsdf sdsdds'
    # 1.1 also user may have forgotten to enter ':' in a valid input, for eg. 'series C 4' or 'series-500 4' - for now this variant will be considered invalid but later
    # some logics may be added to recognise it as valid
    # 2. input contains 1 ':' - we'll get a list with 2 values, the 1st - ds name, the 2nd - ds data // 'series C: 4', 'sdfsdf: sddd', ':'
    # 3. input contains >1 ':' - we'll get a list with >2 values, the 1st will be ds name, the 2nd - ds data, all the rest will be discarded // 'series C: 4, series D: 1, 2, 3, 5,3'
    ds_splitted = ds.split(':')

    if len(ds_splitted) == 1:
        ds_data_part = scatter_data_parse(ds_splitted[0])
    else:
        ds_name = ds_splitted[0].strip()  # any values including empty
        ds_data_part = scatter_data_parse(ds_splitted[1])

    # so we have a part ds_data_part (a list of lists, each with 2 strings supposed to be numbers). variants:
    # 1. correct data (['4', '5']) - result code 'ok'
    # 2. completely incorrect data ([''], ['sdsdd'], ['4.sd'], ['2.3', 'abs']) - result code 'bad'
    # 3. partly correct data (['2', '3'], ['a', 'b']) - results code 'partly'
    # we'll try to convert these data to float numbers, all nondigit values will be substituted with 0
    # in case all series contains only 0s (valid 0s or nondigit values substituted with 0) - result code 'bad'
    floattuple = []
    for strtuple in ds_data_part:
        for item in strtuple:
            try:
                floattuple.append(float(item))
            except ValueError:
                floattuple.append(0)
                result_code = 'partly'
        ds_data.append(tuple(floattuple))
        floattuple = []

    ds_sum = 0
    for everytuple in ds_data:
        for item in everytuple:
            ds_sum += item

    if ds_sum == 0:
        result_code = 'bad'

    # so now we have variants with result codes:
    # 1. 'ok' = a valid number with or without ds name
    # 2. 'partly' = a valid number with or without ds name but user entered >1 value for one ds
    # 3. 'bad' = empty (after deleting delimiters) or non-numeric value
    # p.s. some additional data for response compilation - chart type and subtype
    # We'll return [result_code][message][validated_data_series as dictionary {ds_name: ds_data}]
    chart_type = mychartdata['chart-types']
    chart_name = mychartdata['chartname']

    # we also need to check for previous validated series to display them to user
    if 'validated_ds' in mychartdata:
        already_validated_data = mychartdata['validated_ds'] # is a list of dictionaries "validated_ds": [{"": 1 }, {"": 9}]
        already_validated_data_nice = ' (in addition to series '
        for x in range(len(already_validated_data)):
            for key, value in already_validated_data[x].items():
                if x>0:
                    already_validated_data_nice += ', '
                already_validated_data_nice += '"{}": {}'.format(key, value)
        already_validated_data_nice += '). '
    else:
        already_validated_data_nice = '. '


    if result_code == 'ok':
        output = [
            'ok',
            'Alright! Series "' + ds_name + '": ' + str(ds_data) + " for our " + chart_type + " entitled '" + chart_name + "' received" + already_validated_data_nice,
            {ds_name: ds_data}
        ]
    elif result_code == 'partly':
        output = [
            'partly',
            "Some errors were found in your data. After replacing those errors with 0, we will get '" + ds_name + ": " + str(ds_data) + already_validated_data_nice,
            {ds_name: ds_data}
            ]
    else:
        output = [
            'bad',
            "Invalid data series. Please enter correct data in format 'series name (optionally): series data', for eg. 'TheBigOnes: (1, 2), (2, 4), (3, 5)' or just '(1, 2), (2, 4), (3, 5)'",
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

    # FoodCompositionChatbot action
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

    # PlotBot - input validation action for bar and line charts (user is supposed to enter series name (optionally) and at least 1 number)
    elif action == 'data-series-barline':
        #  get 'contexts'
        contexts = req.get('result').get('contexts')

        # from the 1st context (supposed to be 'mychart') get 'parameters'
        for context in contexts:
            if context['name'] == 'mychart':
                mychartdata = context.get('parameters')

        # get and try to parse and validate data series, in case it's invalid - return error message
        validation_result = get_bar_line_data(mychartdata, 'data-series-0.original')

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

        # Prepare messages for other platforms besides web demo
        outputmessages = [
            {
                "type": 0,
                "platform": "telegram",
                "speech": validation_result[1]
            }
        ]

        if validation_result[0] != 'bad':
            outputmessages.append({
                  "type": 2,
                  "platform": "telegram",
                  "title": "Add another data series or",
                  "replies": [
                    "Build chart",
                    "Restart"
                  ]
                })

        # Compose response
        res = {
            'speech': validation_result[1] + ' Please add another data series or may I draw our chart? If something is wrong please write "restart" to start afresh',
            'displayText': validation_result[1] + ' Please add another data series or may I draw our chart? If something is wrong please write "restart" to start afresh',
            'sourse': 'webhook: data-series-barline',
            'messages': outputmessages,
            'contextOut': outputcontext
        }

    # PlotBot - input validation action for pie chart (user is supposed to enter 1 or several series in format <'series name' (optionally): only 1 number>)
    elif action == 'data-series-pie':
        #  get 'contexts'
        contexts = req.get('result').get('contexts')

        # from the 1st context (supposed to be 'mychart') get 'parameters'
        for context in contexts:
            if context['name'] == 'mychart':
                mychartdata = context.get('parameters')

        # get and try to parse and validate data series, in case it's invalid - return error message
        validation_result = get_pie_data(mychartdata, 'data-series-0.original')

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

        # Prepare messages for other platforms besides web demo
        outputmessages = [
            {
                "type": 0,
                "platform": "telegram",
                "speech": validation_result[1]
            }
        ]

        if validation_result[0] != 'bad':
            outputmessages.append({
                  "type": 2,
                  "platform": "telegram",
                  "title": "Add another data series or",
                  "replies": [
                    "Build chart",
                    "Restart"
                  ]
                })

        # Compose response
        res = {
            'speech': validation_result[1] + ' Please add another data series or may I draw our chart? If something is wrong please write "restart" to start afresh',
            'displayText': validation_result[1] + ' Please add another data series or may I draw our chart? If something is wrong please write "restart" to start afresh',
            'sourse': 'webhook: data-series-pie',
            'messages': outputmessages,
            'contextOut': outputcontext
        }

    # PlotBot - input validation action for pie chart (user is supposed to enter 1 or several series in format <'series name' (optionally): only 1 number>)
    elif action == 'data-series-scatter':
        #  get 'contexts'
        contexts = req.get('result').get('contexts')
        print('Webhook - data-series-scatter')

        # from the 1st context (supposed to be 'mychart') get 'parameters'
        for context in contexts:
            if context['name'] == 'mychart':
                mychartdata = context.get('parameters')
        print('mychartdata: ' + str(mychartdata))

        # get and try to parse and validate data series, in case it's invalid - return error message
        validation_result = get_scatter_data(mychartdata, 'data-series-0.original')
        #print('validation_result: ' + str(validation_result))

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
                        print(validation_result[2])
                        context['parameters']['validated_ds'].append(validation_result[2])
                        print(context['parameters']['validated_ds'])
                    else:
                        print('Here3')
                        print(validation_result[2])
                        context['parameters'].update({'validated_ds': [validation_result[2]]})
                        print(context['parameters']['validated_ds'])
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

        # Prepare messages for other platforms besides web demo
        outputmessages = [
            {
                "type": 0,
                "platform": "telegram",
                "speech": validation_result[1]
            }
        ]

        if validation_result[0] != 'bad':
            outputmessages.append({
                  "type": 2,
                  "platform": "telegram",
                  "title": "Add another data series or",
                  "replies": [
                    "Build chart",
                    "Restart"
                  ]
                })

        # Compose response
        res = {
            'speech': validation_result[1] + ' Please add another data series or may I draw our chart? If something is wrong please write "restart" to start afresh',
            'displayText': validation_result[1] + ' Please add another data series or may I draw our chart? If something is wrong please write "restart" to start afresh',
            'sourse': 'webhook: data-series-pie',
            'messages': outputmessages,
            'contextOut': outputcontext
        }

    # PlotBot - drawing BAR charts webhook
    elif action == 'plotbot-bar':
        # at this stage we have at least 1 already validated data series saved in context 'mychart' in key 'validated_ds'
        contexts = req.get('result').get('contexts')
        for context in contexts:
            if context['name'] == 'mychart':
                charttype = context['parameters']['chart-types']
                chartsubtype = context['parameters']['bar-chart-styles']
                data2plot = context['parameters']['validated_ds'] # is a list for eg. [{"fibo": [1, 2, 4, 8]}, {"next": [2, 3, 4, 5]}]
                chartname = context['parameters']['chartname']

        # to name our chart we'll use last 12 digist of 'id' from JSON got from dialogflow
        ourfilename = 'static/' + req.get('id')[-12:]

        if chartsubtype == 'basic':
            pygal_bar_basic(data2plot, chartname, ourfilename)
        elif chartsubtype == 'horizontal':
            pygal_bar_horizontal(data2plot, chartname, ourfilename)
        elif chartsubtype == 'stacked':
            pygal_bar_stacked(data2plot, chartname, ourfilename)


        # Telegram (and maybe some other platforms) don't insert png images into comments? Let's convert png to jpg..
        '''
        print('ourfilename: ' + ourfilename)
        im = Image.open(ourfilename + ".png")
        rgb_im = im.convert('RGB')
        rgb_im.save(ourfilename + '.jpg')
        '''

        # then we need to return this image's ULR and also update contexts (set lifespan for mychart and ready2chart to 0)
        for context in contexts:
            if context['name'] == 'mychart' or context['name'] == 'ready2plot':
                context['lifespan'] = 0

        # Compose the response to dialogflow.com
        res = {
            'speech': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'displayText': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'source': 'plotbot-bar-webhook',

            'messages': [
                # messages for telegram
                {
                    'type': 0,
                    'platform': 'telegram',
                    'speech': 'Done: here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg, and here\'s a static one: http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    "type": 2,
                    'platform': 'telegram',
                    "title": "What next?",
                    "replies": [
                        "Draw another chart"
                    ]
                },

                # messages for Facebook
                {
                    'type': 3,
                    'platform': 'facebook',
                    'imageUrl': 'http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'And here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'To make another chart type "draw chart" or "restart"'
                }
            ],
            'contextOut': contexts
        }

    # PlotBot - drawing LINE charts webhook
    elif action == 'plotbot-line':
        # at this stage we have at least 1 already validated data series saved in context 'mychart' in key 'validated_ds'
        contexts = req.get('result').get('contexts')
        for context in contexts:
            if context['name'] == 'mychart':
                charttype = context['parameters']['chart-types']
                chartsubtype = context['parameters']['line-chart-styles']
                data2plot = context['parameters']['validated_ds'] # is a list for eg. [{"fibo": [1, 2, 4, 8]}, {"next": [2, 3, 4, 5]}]
                chartname = context['parameters']['chartname']

        # to name our chart we'll use last 12 digist of 'id' from JSON got from dialogflow
        ourfilename = 'static/' + req.get('id')[-12:]

        if chartsubtype == 'basic':
            pygal_line_basic(data2plot, chartname, ourfilename)
        elif chartsubtype == 'horizontal':
            pygal_line_horizontal(data2plot, chartname, ourfilename)
        elif chartsubtype == 'stacked':
            pygal_line_stacked(data2plot, chartname, ourfilename)

        # then we need to return this image's ULR and also update contexts (set lifespan for mychart and ready2chart to 0)
        for context in contexts:
            if context['name'] == 'mychart' or context['name'] == 'ready2plot':
                context['lifespan'] = 0

        # Compose the response to dialogflow.com
        res = {
            'speech': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'displayText': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'source': 'plotbot-bar-webhook',

            'messages': [
                # messages for telegram
                {
                    'type': 0,
                    'platform': 'telegram',
                    'speech': 'Done: here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg, and here\'s a static one: http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    "type": 2,
                    'platform': 'telegram',
                    "title": "What next?",
                    "replies": [
                        "Draw another chart"
                    ]
                },

                # messages for Facebook
                {
                    'type': 3,
                    'platform': 'facebook',
                    'imageUrl': 'http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'And here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'To make another chart type "draw chart" or "restart"'
                }
            ],
            'contextOut': contexts
        }

    # PlotBot - drawing PIE charts webhook
    elif action == 'plotbot-pie':
        # at this stage we have at least 1 already validated data series saved in context 'mychart' in key 'validated_ds'
        contexts = req.get('result').get('contexts')
        for context in contexts:
            if context['name'] == 'mychart':
                charttype = context['parameters']['chart-types']
                chartsubtype = context['parameters']['pie-chart-styles']
                data2plot = context['parameters']['validated_ds'] # is a list if dictionaries for eg. [{"fibo": 1}, {"next": 3}]
                chartname = context['parameters']['chartname']

        # to name our chart we'll use last 12 digist of 'id' from JSON got from dialogflow
        ourfilename = 'static/' + req.get('id')[-12:]

        if chartsubtype == 'basic':
            pygal_pie_basic(data2plot, chartname, ourfilename)
        elif chartsubtype == 'donut':
            pygal_pie_donut(data2plot, chartname, ourfilename)
        elif chartsubtype == 'half pie':
            pygal_pie_halfpie(data2plot, chartname, ourfilename)

        # then we need to return this image's ULR and also update contexts (set lifespan for mychart and ready2chart to 0)
        for context in contexts:
            if context['name'] == 'mychart' or context['name'] == 'ready2plot':
                context['lifespan'] = 0

        # Compose the response to dialogflow.com
        res = {
            'speech': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'displayText': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'source': 'plotbot-bar-webhook',

            'messages': [
                # messages for telegram
                {
                    'type': 0,
                    'platform': 'telegram',
                    'speech': 'Done: here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg, and here\'s a static one: http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    "type": 2,
                    'platform': 'telegram',
                    "title": "What next?",
                    "replies": [
                        "Draw another chart"
                    ]
                },

                # messages for Facebook
                {
                    'type': 3,
                    'platform': 'facebook',
                    'imageUrl': 'http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'And here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'To make another chart type "draw chart" or "restart"'
                }
            ],
            'contextOut': contexts
        }
    # PlotBot - drawing SCATTER charts webhook
    elif action == 'plotbot-scatter':
        # at this stage we have at least 1 already validated data series saved in context 'mychart' in key 'validated_ds'
        contexts = req.get('result').get('contexts')
        for context in contexts:
            if context['name'] == 'mychart':
                charttype = context['parameters']['chart-types']
                data2plot = context['parameters']['validated_ds'] # is a list if dictionaries for eg. [{"fibo": 1}, {"next": 3}]
                chartname = context['parameters']['chartname']

        # to name our chart we'll use last 12 digist of 'id' from JSON got from dialogflow
        ourfilename = 'static/' + req.get('id')[-12:]

        print('Drawing scatter plot...')
        print('data2plot: ' + str(data2plot))
        pygal_scatter(data2plot, chartname, ourfilename)

        # then we need to return this image's ULR and also update contexts (set lifespan for mychart and ready2chart to 0)
        for context in contexts:
            if context['name'] == 'mychart' or context['name'] == 'ready2plot':
                context['lifespan'] = 0

        # Compose the response to dialogflow.com
        res = {
            'speech': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'displayText': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png',
            'source': 'plotbot-bar-webhook',

            'messages': [
                # messages for telegram
                {
                    'type': 0,
                    'platform': 'telegram',
                    'speech': 'Done: here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg, and here\'s a static one: http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    "type": 2,
                    'platform': 'telegram',
                    "title": "What next?",
                    "replies": [
                        "Draw another chart"
                    ]
                },

                # messages for Facebook
                {
                    'type': 3,
                    'platform': 'facebook',
                    'imageUrl': 'http://35.196.100.14/' + ourfilename + '.png'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'And here is an interactive version - http://35.196.100.14/' + ourfilename + '.svg'
                },
                {
                    'type': 0,
                    'platform': 'facebook',
                    'speech': 'To make another chart type "draw chart" or "restart"'
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
# ###################### Decorators END ##############################

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0')#, port=port)

'''
{
    'platform': 'facebook',
    'type': 0,
    'speech': 'Here is our chart: interactive - http://35.196.100.14/' + ourfilename + '.svg and static - http://35.196.100.14/' + ourfilename + '.png'
},
{
    'platform': 'facebook',
    'type': 0,
    'speech': 'To make another chart type "draw chart" or "restart"'
}'''

