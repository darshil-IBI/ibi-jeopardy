import json
import random

def selectQuestion(jsonFilter, data):
    if('category' in jsonFilter):
        print("in category")
        data = [x for x in data if jsonFilter['category'].upper() in x['category'].upper()]
    if('value' in jsonFilter):
        print("in value")        
        if(jsonFilter['value']['range'] == 'higher'):
            print("in higher")
            data = [x for x in data if x['value'] >= jsonFilter['value']['value']]
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

    return ""

def suggestCategory(partialVal, data):
    print('in suggestCategory')
    if(partialVal != ''):
        data = [x for x in data if partialVal.upper() in x['category'].upper()]
    
    suggested = []

    for question in data:
        suggested.append(question['category'])   

    return random.sample(set(suggested), 5)

with open('jeopardy_questions.json') as json_data:
    data = json.load(json_data)
    print(selectQuestion({'show_number': "4999"}, data))
    #print(suggestCategory('', data))

#, 'value': {'value':'$400', 'range': 'higher'}
