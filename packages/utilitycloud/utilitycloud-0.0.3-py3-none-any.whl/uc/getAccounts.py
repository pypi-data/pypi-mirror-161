import requests
import json
import pprint

def getAccounts(token,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }

    apiAction = "account/getaccounts"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.get(urlBuild,headers=headers)
    #print("------LOG------- Asset Classes")
    #pprint.pprint(jaon.loads(response))

    return response

if __name__ == '__main__':
    ""