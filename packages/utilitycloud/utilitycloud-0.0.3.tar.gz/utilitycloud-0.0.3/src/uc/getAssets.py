import requests
import json
import pprint
import time

# MAX count = 1000 assets.  No response at 1001+

def getAssets(token,count,AcctId,IsActive,SearchTerm,*args,**kwargs):
    env = kwargs.get('env','prd')
    url = f"https://api.ucld.us/env/{env}/"
    
    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Authorization':token,
        'contentType': 'application/json'
    }

    payload = json.dumps({
        'Page':kwargs.get('Page',1),
        'ItemCount':count,
        'clientID':AcctId,  #OK - can be left as empty string
        'IsActive':IsActive, #string or boolean is OK
        'SearchFacets':SearchTerm
    })

    apiAction = "asset/getassets"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.post(urlBuild,data=payload,headers=headers)
    try_number=1
    attempts = 10
    while str(response) != "<Response [200]>" and try_number<=attempts:
        print(f"Response from getAssets #{try_number} failed: {str(response)}.  {attempts-try_number} attempts left. Trying again...")
        response = requests.post(urlBuild,data=payload,headers=headers)
        try_number+=1
    #print("------LOG------- Assets")
    #pprint.pprint(response)
    
    return response

def getTotalAssets(token,AcctId,IsActive,SearchTerm):
    page = 1
    count = 500

    response_1 = json.loads(getAssets(token,count,AcctId,IsActive,SearchTerm,Page=page).text)
    assetCount = response_1['body']['TotalCount']
    assetResults = response_1['body']['Assets']
    pages = int(response_1['body']["Pages"])
    print("pages: " + str(pages), ", count: " + str(assetCount))
    while page < pages:
        time.sleep(0.5)
        page += 1
        print(f'page {page} of {pages}')
        fx_response = getAssets(token,count,AcctId,IsActive,SearchTerm,Page=page)
        json_response = json.loads(fx_response.text)
        assetResults.extend(json_response['body']['Assets'])

    return assetResults

if __name__ == "__main__":
    ""