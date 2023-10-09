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
    SYM = symClient()
    return(SYM.http(request,SYM))

def http(request):
    global SYM
    SYM = symClient()
    return(SYM.http(request,SYM))


def cli():
    global SYM
    SYM = symClient()
    return(SYM.cli(sys.argv,SYM))
    
     
    