from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import random
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
jepData = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Hello World!")
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    global jepData

    print("processRequest0")
    question_query = makeQuery(req)

    print(jepData)

    selectedQuestion = selectQuestion(question_query, jepData)

    res = makeWebhookResult(selectedQuestion)
    return res


def makeQuery(req):
    jsonFilter = {}
    result = req.get("result")
    parameters = result.get("parameters")
    category = parameters.get("category")
    value = parameters.get("value")
    qround = parameters.get("round")

    if category is not None and category is not "":
        jsonFilter['category'] = category
    if value is not None and value is not "":
        jsonFilter['value'] = { "value": value, "range": "exact" }
    if qround is not None and qround is not "":
        jsonFilter['round'] = qround

    print(json.dumps(jsonFilter, indent=4))
    return jsonFilter


def makeWebhookResult(data):
    if (data is None):
        return {
            "welcomeText": "Welcome to Jeopardy!"
	}

    qround = data['round']

    speech = "Category: " + data['category'] + " Round: " + qround + (qround != 'Final Jeopardy!' if (" Value: " + data['value']) else '') + "\nQuestion: " + data['question']

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def selectQuestion(jsonFilter, data):
    if('category' in jsonFilter):
        print("in category")
        data = [x for x in data if jsonFilter['category'].upper() in x['category'].upper()]
    if('value' in jsonFilter):
        print("in value")        
        if(jsonFilter['value']['range'] == 'higher'):
            print("in higher")
            data = [x for x in data if x['value'] >= jsonFilter['values']['value']]
        elif(jsonFilter['value']['range'] == 'lower'):
            print("in lower")
            data = [x for x in data if x['value'] <= jsonFilter['value']['value']]
        else:
            print("in exact")
            data = [x for x in data if x['value'] == jsonFilter['value']['value']]
    if('round' in jsonFilter):
        print("in round")
        data = [x for x in data if x['round'] == jsonFilter['round']]
    
    if('question' in jsonFilter):
        print("in question")
        data = [x for x in data if jsonFilter['question'].upper() in x['question'].upper()]        
    
    if('air_date' in jsonFilter):
        print("in question")
        data = [x for x in data if jsonFilter['air_date'] in x['air_date'].upper()]

    if('show_number' in jsonFilter):
        data = [x for x in data if x['show_number'] == jsonFilter['show_number']]

    if(data):
        return random.choice(data)

    return None

def suggestCategory(partialVal, data):
    print('in suggestCategory')
    if(partialVal != ''):
        data = [x for x in data if partialVal.upper() in x['category'].upper()]
    
    suggested = []

    for question in data:
        suggested.append(question['category'])   

    return random.sample(set(suggested), 5)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    contents = open("JEOPARDY_QUESTIONS.json")
    jepData = json.load(contents)

    print(jepData)

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
