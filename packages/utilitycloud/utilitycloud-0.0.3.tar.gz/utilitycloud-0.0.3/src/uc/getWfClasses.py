import requests
import json
from pprint import pprint

def getWfClasses(token,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }

    apiAction = "workflow/getworkflows"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.get(urlBuild,headers=headers)
    response = json.loads(response.text)
    #print("------LOG------- Workflow Classes")
    #pprint(response)

    return response

if __name__ == '__main__':
    ''