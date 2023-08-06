import requests
import json

def getUserRead(token,billingAccountId,ActiveOnly,*args,**kwargs):
  domain = kwargs.get('domain','https://ucld.us/')
  url = domain

  headers = {
      'Accept':'*/*',
      'Accept-Language':'en-US,en;q=0.8',
      'Authorization':token,
      'Content-Type': 'application/json',
      'Accept-Encoding':'gzip, deflate, br'
  }

  body = json.dumps({
      "page":kwargs.get('page',1),
      "itemCount":kwargs.get('itemCount',100),
      "search":kwargs.get('serach',''),
      "orderby":None,
      "isAdvanced":False,
      "filters":None,
      "billingAccountId":str(billingAccountId),
      "facets":"",
      "IsActive":ActiveOnly,
      "active":ActiveOnly,  
      "clientID":"ALL_CLIENTS",
      "IsSimpleSearch":True})

  apiAction = "api/UserDirectoryController/read"
  urlBuild = url+apiAction
  print("------LOG---- URL BUILD "+urlBuild)
  response = requests.post(urlBuild,headers=headers,data=body)
  #print("------LOG------- Workflow Fields")
  #pprint.pprint(response)

  return response

def getUser(token, username,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'contentType': 'application/json'
    }

    apiAction = "user/details?un="+username
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = json.loads(requests.get(urlBuild, headers=headers).text)

    return response

def getUser_raw(token, username,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'contentType': 'application/json'
    }

    apiAction = "user/details?un="+username
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.get(urlBuild, headers=headers)

    return response

if __name__ == '__main__':
    ""