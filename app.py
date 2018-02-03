from flask import Flask, render_template, url_for, request, redirect, flash
import pygal
import cairosvg

app = Flask(__name__)

chart_name = 'Fibonacci'
data = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
png_file_name = 'bar_chart1.png'

def pygal_bar_chart(chart_name, data, png_file_name):
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

    # Check if the request is for the foodcomposition action
    if action == 'plotbot':
        data = req.get('result').get('parameters').get('food')
    '''
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
    else:
        # If the request is not to the translate.text action throw an error
        res = {
            'speech': 'Something wrong happened',
            'displayText': 'Something wrong happened'
        }
    
    return make_response(jsonify(res))
    '''
    print(req)
    return make_response(jsonify(req))

if __name__ == '__main__':
    #port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0')#, port=port)



