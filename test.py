anotherjson = {
  "id": "a1a7f75d-5e41-48d6-82fd-eed4594c5379",
  "timestamp": "2018-02-09T10:20:16.219Z",
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
          "validated_ds": [
            {
              "fibo": [
                1,
                2,
                4,
                8
              ]
            }
          ],
          "chart-types.original": "",
          "data-series-0.original": "fibo: 1, 2, 4, 8",
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
      "webhookResponseTime": 168,
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

for context in anotherjson['result']['contexts']:
  if context['name'] == 'mychart':
    print(context)
    if 'validated_ds' in context['parameters']:
      print('Yes' + str(context['parameters']['validated_ds']))