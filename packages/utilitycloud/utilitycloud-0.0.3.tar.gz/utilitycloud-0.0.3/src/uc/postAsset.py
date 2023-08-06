import requests
import json
from datetime import datetime
from .getUser import getUser
from .getWoById import getWoById


# def postAsset(token, user, wo_id, wfid, aid, fields):

#     try:
#         user_response = getUser(token, user)
#         user_guid = user_response['LegacyId']
#         user_full_name = user_response['User']['Name']
#     except:
#         print("KEY ERROR LEGACY ID")
#         print(user_response)

#     right_now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

#     response = postAsset_payload(token, right_now, user_guid, user, user_full_name, aid, wfid, wo_id, fields)
#     return response


# def postAsset_payload(token, right_now, user_guid, user, user_full_name, aid, wfid, wo_id, fields):
#     payload = json.dumps(
#         {
#             "ReportId": 0,
#             "ReportDate": right_now,
#             "ReportAuthorId": user_guid,
#             "ReportAuthorUsername": user,
#             "ReportAuthorFullname": user_full_name,
#             "ReportSignature": None,
#             "ReportParentId": None,
#             "AssetId": aid,
#             "WorkflowId": wfid,
#             "WorkOrderId": wo_id,
#             "ReportData": fields,
#             "FiledInSequence": False,
#             "SequenceAssetAssetId": 0,
#             "WorkflowReportKey": None,
#             "WorkflowReportKey": None,  #"wf_53207656_a_696815688_u_cfd0d767-2d3e-4c36-b99b-1bc800dc8165_2020-02-19T15:35:24.011Z_wo_200009637"
#             "BatchId": None,
#             "WorkQueueListId": None
#         }
#     )
#     # print(payload)

#     response = postAsset_raw(token, payload)
#     return response


def postAsset_raw(token, payload,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token,
        'contentType': 'application/json'
    }
    payload = json.dumps(payload)

    apiAction = "asset/postasset"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild, data=payload, headers=headers)
    #print("------LOG------- WorkOrders")
    # pprint.pprint(response)

    return response