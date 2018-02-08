myinput = {
  "id": "08b0c944-78cb-4984-af16-197783116022",
  "timestamp": "2018-02-08T10:32:24.87Z",
  "lang": "en",
  "result": {
    "source": "agent",
    "resolvedQuery": "fibonacci: 1, 2, 3, 4, 5",
    "action": "data-series-0",
    "actionIncomplete": False,
    "parameters": {
      "data-series-0": "fibonacci 1 2 3 4 5"
    },
    "contexts": [{'name': 'barchart-followup-2', 'parameters': {'bar-chart-styles': 'basic', 'chart-types': 'bar chart', 'chart-types.original': '', 'data-series-0.original': 'fibonacci: 1, 2, 3, 4, 5', 'data-series-0': 'fibonacci 1 2 3 4 5', 'bar-chart-styles.original': 'basic'}, 'lifespan': 0}, {'name': 'barchart-followup-3', 'parameters': {'bar-chart-styles': 'basic', 'chart-types': 'bar chart', 'chart-types.original': '', 'data-series-0.original': 'fibonacci: 1, 2, 3, 4, 5', 'data-series-0': 'fibonacci 1 2 3 4 5', 'bar-chart-styles.original': 'basic'}, 'lifespan': 0}, {'name': 'mychart', 'parameters': {'bar-chart-styles': 'basic', 'chart-types': 'bar chart', 'chart-types.original': '', 'data-series-0.original': 'fibonacci: 1, 2, 3, 4, 5', 'data-series-0': 'fibonacci 1 2 3 4 5', 'bar-chart-styles.original': 'basic'}, 'lifespan': 5}, {'name': 'bar-basic-dataseries-add0-followup', 'parameters': {'data-series-0.original': 'fibonacci: 1, 2, 3, 4, 5', 'data-series-0': 'fibonacci 1 2 3 4 5'}, 'lifespan': 2}, {'name': 'barchart-followup', 'parameters': {'bar-chart-styles': 'basic', 'chart-types': 'bar chart', 'chart-types.original': '', 'data-series-0.original': 'fibonacci: 1, 2, 3, 4, 5', 'data-series-0': 'fibonacci 1 2 3 4 5', 'bar-chart-styles.original': 'basic'}, 'lifespan': 0}, {'name': 'ready2plot', 'parameters': {'data-series-0.original': 'fibonacci: 1, 2, 3, 4, 5', 'data-series-0': 'fibonacci 1 2 3 4 5'}, 'lifespan': 5}],
    "metadata": {
      "intentId": "52ed7917-6920-4c68-b6e7-55ef6562d6ce",
      "webhookUsed": "true",
      "webhookForSlotFillingUsed": "false",
      "webhookResponseTime": 174,
      "intentName": "bar - basic - data.series - add0"
    },
    "fulfillment": {
      "speech": "Alright! fibonacci: 1, 2, 3, 4, 5 for our basic bar chart received.",
      "messages": [
        {
          "type": 0,
          "platform": "telegram",
          "speech": "Alright! fibonacci: 1, 2, 3, 4, 5 for our basic bar chart received."
        },
        {
          "type": 0,
          "platform": "telegram",
          "speech": "Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh"
        },
        {
          "type": 0,
          "speech": "Alright! fibonacci: 1, 2, 3, 4, 5 for our basic bar chart received."
        },
        {
          "type": 0,
          "speech": "Add another data series (please follow the same format, 'Fibonacci: 1, 2, 4, 8, 16, 32') or let's draw our chart? If something is wrong please write 'restart' to start afresh"
        }
      ]
    },
    "score": 1
  },
  "status": {
    "code": 206,
    "errorType": "partial_content",
    "errorDetails": "Webhook call failed. Error: 500 INTERNAL SERVER ERROR",
    "webhookTimedOut": False
  },
  "sessionId": "55ae83c3-7561-4978-9b2e-a0e4282e1591"
}

print(myinput['result']['contexts'])
for context in myinput['result']['contexts']:
    if context['name'] == 'mychart':
        print('Hello')
