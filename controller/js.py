import os
import requests
import json 

def help():
    return """source=SOURCE_NAME 
    body : {
        "subTime":1580000000
    }

    return : {
         "subTime":1580000000,
         "next" : 100 
    }
    dest=DEST_NAME 
    body : {
    "request": {
            "id_s": {
                [ID_S]
            },
            "properties": {
                [PROPERTIES]
            },
        }
    }
    return : {
        "id_s": {
            [ID_S]
        }
    }
    """

def run(request,SYM):
    n = 0
    getUrl = ""
    for get in request['get']:
        if n == 0:
            getUrl = getUrl + "?"+get+"="+request['get'][get]
        else:
            getUrl = getUrl + "&"+get+"="+request['get'][get]
        n += 1
    url = os.getenv('jsSYM_URL')+getUrl

    payload = json.dumps(request['body'])

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return(response.json())
