import requests
import json
import pprint
from uc.getUser import getUser

# MAX count = 1000 assets.  No response at 1001+

def getWos(token,user,SearchFacets,page,count,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }
    
    if isinstance(user, str):
        baid = getUser(token,user)['User']['BillingAccountId']
        print(f"getWos Billing Account ID search: {baid}")
    else:
        baid = user

    payload = json.dumps({ 
        'billingAccountId': baid,
        'facets': SearchFacets,
        'filters': None,
        'isAdvanced': True,
        'itemCount': count,
        'orderby': None,
        'page': page,
        'search': ""
    })

    apiAction = "workorder/getworkorders"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = json.loads(requests.post(urlBuild,data=payload,headers=headers).text)
    #print("------LOG------- WorkOrders")
    #pprint.pprint(response)
    
    return response
    
"""
payload = json.dumps({
    'IsActive': True,
    'IsSimpleSearch': False,
    'active': True,
    'billingAccountId': "150",
    'clientID': "MY_CLIENTS",
    'facets': "",
    'filters': None,
    'isAdvanced': False,
    'itemCount': "25",
    'orderby': None,
    'page': 1,
    'search': ""
})
"""

def getTotalWos(token,user,search):
    page = 1
    count = 1000
    #getWos(token,user,SearchFacets,page,count)
    baid = getUser(token,user)['User']['BillingAccountId']
    print(f"getWos Billing Account ID search: {baid}")

    response = getWos(token,baid,search,page,count)
    #pprint.pprint(response)
    woCount = response["totalResults"]
    woResults = response["WorkOrders"]
    pages = int(response["totalPages"])
    print("pages: " + str(pages), ", count: " + str(woCount))
    while page < pages:
        page += 1
        response = getWos(token,baid,search,page,count)
        woResults.extend(response["WorkOrders"])
        #print(len(woResults))

    return woResults


def convertWoHeaders(wo_dataframe):
  wo_header_conversions=[
    {'ID':'Work Order ID'},
    {'ttl':'Workflow Title'},
    {'aaid':'Account ID'},
    {'ades':'Asset Description'},
    {'atag':'Asset Tag'},
    {'aid':'Asset ID'},
    {'baid':'Billing Account ID'},
    {'wou':'Work Order Assignees'}, #Note this is a List/Array
    {'sd':'Start Date'},
    {'dd':'Date Due'},
    {'des':'Work Order Description'},
    {'dm':'Date Modified'},
    {'ed':'End Date'},
    {'ifail':'Asset Class Fail Icon'},
    {'pid':'Project ID'},
    {'pri':'Work Order Priority'},
    {'sta':'Work Order Status'},
    {'stid':'Work Order Status ID'},
    {'typ':'Work Order Type'},
    {'dc':'Date Created'},
    {'wfid':'WorkflowID'},
  ]
  new_wo_dataframe = wo_dataframe.rename(wo_header_conversions)
  return new_wo_dataframe