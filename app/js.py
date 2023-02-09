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
    for get in request['body']['node']['get']:
        if n == 0:
            getUrl = getUrl + "?"+get+"="+request['body']['node']['get'][get]
        else:
            getUrl = getUrl + "&"+get+"="+request['body']['node']['get'][get]
        n += 1
    url = os.getenv('jsSYM_URL')+getUrl

    payload = json.dumps(list(request['body']['node']['request'].find({}))[0],default=str)

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return(response.json())
