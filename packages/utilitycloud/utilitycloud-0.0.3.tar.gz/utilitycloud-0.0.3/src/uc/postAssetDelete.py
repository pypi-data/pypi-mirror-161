import json
import requests

def AssetDelete(token,assets,*args,**kwargs):
  domain = kwargs.get('domain','https://ucld.us/')
  headers = {
      'Accept':'*/*',
      'Accept-Language':'en-US,en;q=0.8',
      'Authorization':token,
      'Content-Type': 'application/json',
      'Accept-Encoding':'gzip, deflafdte, br'
  }

  body = json.dumps({
    'assetIds':assets
  })

  apiAction = "api/AccountDetailsController/DELETE_ASSETS"
  urlBuild = domain + apiAction
  print("------LOG---- URL BUILD "+urlBuild)
  response = requests.post(urlBuild,headers=headers,data=body)
  #print("------LOG------- Workflow Fields")
  #pprint.pprint(response)

  return response

if __name__ == "__main__":
  ''