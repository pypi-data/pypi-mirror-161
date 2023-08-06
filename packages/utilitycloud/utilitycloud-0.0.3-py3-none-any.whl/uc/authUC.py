import json
import requests
import boto3

def auth_UC(usern,passw,*args,**kwargs):
    env = kwargs.get('env','prd')
    authURL = f"https://api.ucld.us/env/{env}/authentication"
    authCreds = json.dumps({
        'UserName':usern,
        'Password':passw
    })
    print(f"auth_UC: {usern}")

    headers = {
        'Accept':'*/*',
        'Accept-Language':'en-US,en;q=0.8',
        'Accept-Enconding':'gzip,deflate,br',
        'Content-Type':'application/json'
    }
    auth_try_number=1
    auth_attempts = 10
    response = requests.post(authURL,data=authCreds,headers=headers)
    while str(response) != "<Response [201]>" and auth_try_number<=auth_attempts:
        print(f"Response {auth_try_number} failed: {str(response)}.  {auth_attempts-auth_try_number} attempts left. Trying again...")
        response = requests.post(authURL,data=authCreds,headers=headers)
        auth_try_number+=1
        
    return response



def auth_UCdb(project,*args,**kwargs):
    response_style = kwargs.get('response','list')
    aws_query = kwargs.get('aws',False)
    Billing_Account = project
    
    if aws_query:
        client = boto3.client('lambda', region_name='us-east-1')
        request_project = {
            'Project':Billing_Account
        }
        response = client.invoke(
            FunctionName = 'arn:aws:lambda:us-east-1:871755881625:function:testPyodbc2RDS', 
            InvocationType = 'RequestResponse',
            Payload = json.dumps(request_project)
        )
        responseFromAWS = json.load(response['Payload'])
        user = responseFromAWS["user"]
        passw = responseFromAWS["passw"]
        env = responseFromAWS["env"]
        domain = responseFromAWS["domain"]
        
    token = auth_UC(user,passw,env=env).text
    json_response = {
        'token':token,
        'user':user,
        'passw':passw,
        'env':env,
        'domain':domain
    }
    if response_style == 'json':
        result = json_response
    else:
        result = [token,user,env,domain]
    return result

if __name__ == '__main__':
    ""