import requests
import json
from datetime import datetime
from .getUser import getUser
from .getWoById import getWoById

def postWo(token,user,wo_id,wfid,aid,pri,dc,dm,dd,ed,des,typ,sta,wou):
    
    try:
        user_guid = getUser(token,user)
        user_guid = user_guid['LegacyId']
    except:
        print("KEY ERROR LEGACY ID")
        print(user_guid)
    
    mod_user = user_guid

    wou_guid = []
    for wou_user in wou:
        if wou_user != '':
            wou_user_data = getUser(token,wou_user)
            if wou_user_data.get('LegacyId') != 'LegacyId':
                try:
                    wou_guid.append(wou_user_data['LegacyId'])
                except:
                    print("KEY ERROR LEGACY ID")
                    print(wou_user_data)
            else:
                continue
        else:
            continue
    if wo_id == 0:
        create_u = user_guid
    else:
        create_u = user_guid #getWoById(token,wo_id)['CreatedBy']  #something is funky with this getWoById call

    right_now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    response = postWo_payload(token,user_guid,create_u,mod_user,right_now,wo_id,wfid,aid,pri,dc,dm,dd,ed,des,typ,sta,wou_guid)
    return response

def postWo_payload(token,user_guid,create_u,mod_u,right_now,wo_id,wfid,aid,pri,dc,dm,dd,ed,des,typ,sta,wou_guid):
    payload = json.dumps({
        "WorkOrderID": wo_id,
        "WorkFlowID": wfid,
        "AssetID": aid,
        "Priority": pri,
        "DateCreated": dc,
        "DateModified": right_now,
        "DateDue": right_now,
        #"EndDate": right_now, #dont need this
        "CreatedBy": create_u,
        "ModifiedBy": mod_u,
        "ProjectID": "00000000-0000-0000-0000-000000000000",
        "Description": des,
        "Type": typ,
        "IntervalKey": "",
        "Status": sta,
        #"AssignedToList": [],
        "PostMessage": True
    })
    #print(payload)

    response = postWo_raw(token,payload)
    return response

def postWo_raw(token,payload,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }

    apiAction = "workorder"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild,data=payload,headers=headers)
    #print("------LOG------- WorkOrders")
    #pprint.pprint(response)
    
    return response