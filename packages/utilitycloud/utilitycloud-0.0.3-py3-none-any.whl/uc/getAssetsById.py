import requests
import json
import pprint

def getAssetsById(token,asset_id,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }
    parameters = {
        'assetid':asset_id
    }
    apiAction = "asset/getassetbyid"
    urlBuild = url+apiAction
    response = requests.get(urlBuild,params=parameters,headers=headers)
    print("------LOG---- URL BUILD "+response.url)
    #print("------LOG------- Assets")
    #pprint.pprint(response)
    
    return response.text