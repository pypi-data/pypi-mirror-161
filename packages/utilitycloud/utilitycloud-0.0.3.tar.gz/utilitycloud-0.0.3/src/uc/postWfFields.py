import requests
import json
import pprint

#look at workflow 53207602 in base W&C billing account for type definitions

def postWfFields(token,payload,*args,**kwargs):
  domain = kwargs.get('domain','https://ucld.us/')
  url = domain


  headers = {
      'Accept':'*/*',
      'Accept-Language':'en-US,en;q=0.8',
      'Authorization':token,
      'Content-Type': 'application/json',
      'Accept-Encoding':'gzip, deflate, br'
  }
 
  body = json.dumps(payload)

  apiAction = "api/WorkFlowDetailsController/SAVE_WORKFLOW_DETAILS"
  urlBuild = url+apiAction
  print("------LOG---- URL BUILD "+urlBuild)
  response = requests.post(urlBuild,headers=headers,data=body)
  #print("------LOG------- Workflow Fields")
  #pprint.pprint(response)

  return response