# this is the version working at 'chatbots' VM in GC
# contains webhooks and functions for 2 chatbots:
# - PlotBot (https://github.com/IuriiD/plotbot ; PB) and
# - FoodCompositionChatBot (https://github.com/IuriiD/food_composition_chatbot ; CFB)

import json
import requests
from flask import Flask, request, make_response, jsonify
import ast # TestBot

app = Flask(__name__)

# ###################### Decorators #########################################
@app.route('/')
def index():
    return 'Webhooks for chatbots Plotbot and FoodCompositionChatBot'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get request parameters
    req = request.get_json(silent=True, force=True)
    action = req.get('result').get('action')

    # TestBot (currently "BalanceBot")
    if action == "testbot":
        # Get our log (txt file will be substituted with Mongo DB)
        with open("log.txt", "r+") as logfromtxt:
            log = ast.literal_eval(logfromtxt.read())

        BASIC_CURRENCY = 'UAH'
        # Exchange rates to be substituted with calls to some API
        usd_uah = 26.9
        eur_uah = 33.1

        user1 = req.get('result').get('parameters').get('user1')
        user2 = req.get('result').get('parameters').get('user2')
        sum = req.get('result').get('parameters').get('sum')  # {"amount": 100, "currency": "USD"}
        sum_basic_currency = req.get('result').get('parameters').get('sum_basic_currency')
        timestamp = req.get('timestamp')

        print('user1: ' + user1)
        print('user2: ' + user2)
        print('sum: ' + str(sum))
        print('sum_basic_currency: ' + str(sum_basic_currency))

        # If currency != basic (for eg., UAH), convert to basic currency
        amount = 0
        if sum == "":
            amount = sum_basic_currency
        else:
            if sum["currency"] == BASIC_CURRENCY:
                amount = sum["amount"]
            elif sum["currency"] == "USD":
                amount = sum["amount"] * usd_uah
            elif sum["currency"] == "EUR":
                amount = sum["amount"] * eur_uah

        print('sum_converted: ' + str(amount))

        # In our 1st model we'll have 2 already registered users, Tim and Dan
        if user2 == "":  # means that user1 paid for all = he gets his sum - sum/users_quantity, for eg. if 2 users and user1 paid $50, his balance will be +25$
            who_received = "all"
            every_user_gets = amount / len(log["users"])

        print("log: " + str(log))

        nexttransaction = {
            "timestamp": timestamp,
            "transaction_number": len(log["transactions"]) + 1,
            "who_paid": user1,
            "who_received": who_received,
            "amount": amount,
            "transaction_balance": {},
            "total_balance": {}
        }

        for user in log["users"]:
            if user != user1:
                nexttransaction["transaction_balance"].update({user: every_user_gets * -1})
                user_balance_was = log["transactions"][len(log["transactions"]) - 1]["total_balance"][user]
                user_balance_now = user_balance_was + every_user_gets * -1
            else:
                nexttransaction["transaction_balance"].update({user: amount - every_user_gets})
                user_balance_was = log["transactions"][len(log["transactions"]) - 1]["total_balance"][user]
                user_balance_now = user_balance_was + amount - every_user_gets
            print("Balance of user {} was {}, became {}".format(user, user_balance_was, user_balance_now))
            nexttransaction["total_balance"][user] = user_balance_now

        print("nexttransaction: " + str(nexttransaction))

        log["transactions"].append(nexttransaction)
        print("New log: " + str(log))

        with open("log.txt", "w") as logdump:
            logdump.write(str(log))

        ourspeech = "Balance: " + str(log["transactions"][len(log["transactions"]) - 1]["total_balance"])

        res = {
            'speech': ourspeech,
            'displayText': ourspeech,
            'source': 'webhook: testbot',

            'messages': [
                {
                    'type': 0,
                    'platform': 'telegram',
                    'speech': ourspeech
                },
                {
                    'type': 0,
                    'speech': ourspeech
                }
            ],
            'contextOut': req['result']['contexts']
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