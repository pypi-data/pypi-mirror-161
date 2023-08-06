import requests
import json
import pprint

def getWoById(token,Id,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }

    apiAction = "workorder?workorderid="
    urlBuild = url + apiAction + str(Id)
    print("------LOG---- URL BUILD "+urlBuild)
    response = json.loads(requests.get(urlBuild,headers=headers).text)
    #pprint.pprint(response)

    return response