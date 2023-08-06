import requests
import json

def closeWo(token,woid,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }

    apiAction = "workorder/closeworkorder?workorderid="
    urlBuild = url+apiAction+str(woid)
    print("------LOG---- URL BUILD "+urlBuild)
    response = json.loads(requests.post(urlBuild,headers=headers).text)
    #print("------LOG------- WorkOrders")
    #pprint.pprint(response)
    
    return response