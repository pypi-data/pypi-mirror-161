import requests
import json
import pprint

#look at workflow 53207602 in base W&C billing account for type definitions

def getWfRead(token,workflowId,*args,**kwargs):
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
    'workflowid':str(workflowId)
  })

  apiAction = "api/WorkflowDetailsController/Read"
  urlBuild = url+apiAction
  print("------LOG---- URL BUILD "+urlBuild)
  response = requests.post(urlBuild,headers=headers,data=body)
  #print("------LOG------- Workflow Fields")
  #pprint.pprint(response)

  return response


def getWfFields(token,workflowId,*args,**kwargs):
  env = kwargs.get('env','prd')
  url = f"https://api.ucld.us/env/{env}/"

  headers = {
      'Accept':'*/*',
      'Accept-Language':'en-US,en;q=0.8',
      'Authorization':token,
      'contentType': 'application/json'
  }

  apiAction = "workflow/getworkflowfields?workflowid=" + str(workflowId)
  urlBuild = url+apiAction
  print("------LOG---- URL BUILD "+urlBuild)
  response = requests.get(urlBuild,headers=headers)
  #print("------LOG------- Workflow Fields")
  #pprint.pprint(response)

  return response

def convertFieldTypeId(field_id):
  field_index = int(field_id)-1
  conversions=[
    {'Type':1, 'Title':'Text', 'DB_type':'varchar(255)'},
    {'Type':2, 'Title':'Number', 'DB_type':'float(53)'},
    {'Type':3, 'Title':'Multiple Choice', 'DB_type':'varchar(255)'},
    {'Type':4, 'Title':'True/False', 'DB_type':'bit'},
    {'Type':5, 'Title':'Memo', 'DB_type':'varchar(max)'},
    {'Type':6, 'Title':'Email', 'DB_type':'varchar(255)'},
    {'Type':7, 'Title':'Telephone', 'DB_type':'varchar(255)'},
    {'Type':8, 'Title':'Date', 'DB_type':'datetime'},
    {'Type':9, 'Title':'Time', 'DB_type':'time'},
    {'Type':10, 'Title':'Datetime', 'DB_type':'datetime'},
    {'Type':11, 'Title':'Photo', 'DB_type':'varchar(255)'},
    {'Type':12, 'Title':'Heading', 'DB_type':'varchar(255)'},
    {'Type':13, 'Title':'QR Code', 'DB_type':'varchar(max)'},
    {'Type':14, 'Title':'Multi Select', 'DB_type':'varchar(max)'},
    {'Type':15, 'Title':'JSON Storage', 'DB_type':'varchar(max)'},
    {'Type':16, 'Title':'Additional Report Emails', 'DB_type':'varchar(max)'},
    {'Type':17, 'Title':'Expression', 'DB_type':'varchar(255)'},
    {'Type':18, 'Title':'Signature', 'DB_type':'varchar(255)'},
    {'Type':19, 'Title':'Users', 'DB_type':'varchar(max)'},
    {'Type':20, 'Title':'Location', 'DB_type':'varchar(max)'},
    {'Type':21, 'Title':'Asset', 'DB_type':'varchar(255)'},
    {'Type':22, 'Title':'Asset Class', 'DB_type':'varchar(255)'},
    {'Type':23, 'Title':'Account', 'DB_type':'varchar(255)'}
  ]
  return conversions[field_index]['Title']

if __name__ == '__main__':
  ''