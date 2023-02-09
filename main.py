
import traceback
import base64
import json
import os
import requests
from SYM import symClient
import sys
from dotenv import load_dotenv
from pathlib import Path
import functions_framework
load_dotenv()
dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

@functions_framework.http
def local(request):
    global SYM
    SYM = symClient(os.getenv('MONGODB'),os.getenv('LOCAL_LINK'),os.getenv('DB'),"certifi")
    return(SYM.http(request))

def http(request):
    global SYM
    SYM = symClient(os.getenv('MONGODB'),os.getenv('PROD_LINK'),os.getenv('DB'))
    return(SYM.http(request))

def pubSub(event, context):
    global SYM
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    request = json.loads(pubsub_message)
    SYM = symClient(os.getenv('MONGODB'),os.getenv('PROD_LINK'),os.getenv('DB'))
    SYM.pubSub(request)

def cli():
    global SYM
    SYM = symClient(os.getenv('MONGODB'),os.getenv('LOCAL_LINK'),os.getenv('DB'),"certifi")
    return(SYM.cli(sys.argv))
    
     
    