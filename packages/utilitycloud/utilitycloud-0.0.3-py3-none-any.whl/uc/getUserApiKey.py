import requests
import json
import pprint

def getUserApiKey(token, username, *args, **kwargs):
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
    print("------LOG----- User Details")
    # pprint.pprint(response['UserApiKeyDetail'])
    apiKey = response['UserApiKeyDetail']['UserApiKey']['ApiKey']
    print(apiKey)

    return apiKey
