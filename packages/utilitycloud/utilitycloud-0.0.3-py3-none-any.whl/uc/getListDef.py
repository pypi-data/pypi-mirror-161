import requests
import json

def getLists(token,*args,**kwargs):
    domain = kwargs.get('domain','https://ucld.us/')
    url = domain

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    body = json.dumps({
        "IsActive": True
        ,"IsSimpleSearch": True
        ,"active": True
        ,"billingAccountId": "181"
        ,"clientID": ""
        ,"facets": ""
        ,"filters": None
        ,"isAdvanced": False
        ,"itemCount": "100"
        ,"orderby": None
        ,"page": 1
        ,"search": ""
    })

    apiAction = "api/ListDefDirectoryController/Read"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild, headers=headers, data=body)
    #print("------LOG------- Workflow Fields")
    # pprint.pprint(response)

    return response


def getList(token, listid,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    body = json.dumps({
        "listid": str(listid)
    })

    apiAction = "ListDefDetailsController/Read"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild, headers=headers, data=body)
    #print("------LOG------- Workflow Fields")
    # pprint.pprint(response)

    return response

    # ListDefDetailsController/UPDATELIST


def updateList(token, body,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    # this below variable is an example payload
    example_body = json.dumps({
        "listid": -1, "list": {
            "ListID": -1
            ,"Name": "True/False"
            ,"IsActive": True
            ,"hasParent": False
            ,"ParentName": ""
            ,"ParentListID": None
            ,"BillingAccountID": 181
        }
    })

    apiAction = "ListDefDetailsController/UPDATELIST"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild, headers=headers, data=body)
    #print("------LOG------- Workflow Fields")
    # pprint.pprint(response)

    return response


def updateListItem(token, listItem,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    example_listItem = json.dumps({
        "listid": 51011650
        ,"listitem": {
            "ListItemID": ''#ListItemId
            ,"Value": "True"
            ,"ParentListItemID": None
            ,"IsActive": True
            ,"IsImpersonate": False
            ,"ListItemKey": ""
            ,"SortOrder": 10
            ,"hasParent": False
            , "ParentListID": None
            ,"ParentName": ""
            }
        })

    apiAction = "ListDefDetailsController/UPDATELISTITEM"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild, headers=headers, data=listItem)
    #print("------LOG------- Workflow Fields")
    # pprint.pprint(response)

    return response


if __name__ == '__main__':
    ""