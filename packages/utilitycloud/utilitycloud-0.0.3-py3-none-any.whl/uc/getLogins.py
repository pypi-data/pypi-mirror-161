import requests
import json

#"search":kwargs.get('serach',''),
def getLogins(token,*args,**kwargs):
    domain = kwargs.get('domain','https://ucld.us/')
    url = domain

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Authorization': token
        #'contentType': 'application/x-www-form-urlencoded'
    }

    data = {
        'txtSrtDate': '7/1/2020',
        'txtEndDate': '9/1/2020',
        'btnGetData': 'Update'
    }
    apiAction = "api/Members/WhiteLabelMonthlyBillingReport.aspx"
    urlBuild = url+apiAction
    print("------LOG---- URL BUILD "+urlBuild)
    response = requests.get(urlBuild, headers=headers)

    return response

if __name__ == '__main__':
    ''
