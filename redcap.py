import os
import requests
import json

token = None
endpoint = None
theOR = None
def load_token():
    theFile = os.path.join(os.path.dirname(__file__), "token.auth")
    f = open(theFile)
    for ind, line in enumerate(f):
        if(ind == 0):
            global theOR
            theOR = line.strip("\n")
        elif(ind == 1):
            global endpoint
            endpoint = line.strip("\n")
        elif(ind == 2):
            global token
            token = line.strip("\n")
    f.close()
load_token()

def post_redcap(theDatas):
    global token
    global endpoint
    global theOR
    if(token == None or endpoint == None or theOR == None): 
        return(None)
    
    try:
        data = {
            'token': token,
            'content': 'record',
            'action': 'import',
            'format': 'json',
            'type': 'flat',
            'overwriteBehavior': 'normal',
            'forceAutoNumber': 'true',
            'data': '',
            'returnContent': 'count',
            'returnFormat': 'json'
        }

        theSendStruct = {'record_id': 0, 'or': theOR}
        for key in theDatas:
            theSendStruct[key] = theDatas[key]
        data['data'] = json.dumps([theSendStruct])

        r = requests.post(endpoint, data=data)

        if(r.status_code != 200):
            print(r.json())
            return(-2)
        elif(r.status_code == 200 and r.json()['count'] != 1):
            print(r.json())
            return(-1)
        else:
            return(1)
    except Exception as err:
        print("post_redcap:", err)
        return(-3)

