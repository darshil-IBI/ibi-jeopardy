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
currentQuestion = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    print('in webhook')
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    result = req.get("result")
    parameters = result.get("parameters")	
	
    speech = ""

    if(parameters.get("playJeopardy")):
        speech = processHelloRequest(parameters)
    elif(parameters.get('suggestCategories')):
        speech = processSuggestionRequest(parameters)
    elif(parameters.get('answer')):
        speech = processAnswerRequest(parameters)
    else:
        speech = processQuestionRequest(parameters)
    
    res = makeWebhookResult(speech)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(speech):
    print("in makeWebHookResult")
    print(speech)

    if (speech == ''):
        return {
            "speech": "Hi. I'm the Jeopardy bot. Want to play?"
	    }

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }

def processQuestionRequest(parameters):
    print('processQuestionRequest')
    global jepData
    global currentQuestion

    question_query = makeQuery(parameters)
    currentQuestion = selectQuestion(question_query, jepData)

    print (currentQuestion)
    if(currentQuestion is not None):
        return "Category: " + currentQuestion['category'] + " Round: " + currentQuestion['round'] + (" Value: " + currentQuestion['value'] if (currentQuestion['round'] != 'Final Jeopardy!') else '') + "\nQuestion: " + currentQuestion['question']
    
    return "Couldn't find anything with those requirements."

def processHelloRequest(parameters):
    print ('in processHelloRequest')
    global currentQuestion
    currentQuestion = {}

    return "Ready when you are!"


def processSuggestionRequest(parameters):
    print('in processSuggestionRequest')
    global jepData
    suggested = []

    for question in jepData:
        suggested.append(question['category'])   

    return ", ".join(random.sample(set(suggested), 5))

def processAnswerRequest(parameters):
    print('in processAnswerRequest')
    global currentQuestion

    answer = parameters.get("answer")
    if(answer.endswith("?")):
        answer = answer[:-1]
    if(currentQuestion is None):
        return "The is no question to answer!"
    #elif(answer.upper() in currentQuestion['answer'].upper()):
    #    currentQuestion = {}
    return "You are Correct!" if (answer.upper() in currentQuestion['answer'].upper()) else "Incorrect answer!"

def makeQuery(parameters):
    print('in makeQuery')
    jsonFilter = {}
    category = parameters.get("category")
    value = parameters.get("value")
    qround = parameters.get("round")
    air_date = parameters.get("air_date")

    print("Category:" + category)
    print("Value:" + value)

    if(category is not None and category != ""):
        jsonFilter['category'] = category
    if (value is not None and value != ""):
        if(not value.startswith("$")):
            value = "$" + value
        jsonFilter['value'] = { "value": value, "range": "exact" }
    if (qround is not None and qround != ""):
        jsonFilter['round'] = qround
    if (air_date is not None and air_date != ""):
        jsonFilter['air_date'] = air_date
    print("jsonfilter")
    print(jsonFilter)
    return jsonFilter




def selectQuestion(jsonFilter, data):
    print('in selectQuestion')
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


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) 

    contents = open("JEOPARDY_QUESTIONS.json")
    jepData = json.load(contents)

    print('Jeopardy data loaded. Ready to rock!')
    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
