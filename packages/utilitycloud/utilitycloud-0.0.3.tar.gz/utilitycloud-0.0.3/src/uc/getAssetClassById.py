import requests
import json
import pprint

##sometimes this API returns a blank response and needs to be called multiple times

def getAssetClassById(token,asset_class_id,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json',
        'User-Agent':'Python'
    }
    cookie = {}

    parameters = {
        'csid':asset_class_id
    }

    apiAction = "assetclass/getassetclassbyid"
    urlBuild = url+apiAction
    response = requests.get(urlBuild,headers=headers,params=parameters)
    print("------LOG---- URL BUILD "+response.url)
    #print("------LOG------- Asset Classes")
    #pprint.pprint(json.loads(response))

    return response