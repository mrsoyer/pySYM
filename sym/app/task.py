import base64

import requests
import json
import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne, DeleteOne
from google.cloud import pubsub_v1
from google.oauth2 import service_account
import requests
import json
import traceback
from bson import json_util
import datetime
from datetime import  date, timedelta
import pytz

def valArray(val,Array):
    try:
        return Array[val]
    except:
        return ""



def findValueArray(sets,find):
    dEx = find.split("$.")

    find = find.split(".")
    val = sets
    ret = []
    dol = 0
    for f in find:
        if f == "$":
            dol = 1
            ret = []
            for v in val:
                if len(dEx) == 1:
                    ret.append(v)
                else:
                    #print(dEx[1])
                    #die()
                    ret.append(findValueArray(v,dEx[1])[0])
        if dol == 0:
            if f.isnumeric() == True:
                f = int(f)
            val = valArray(f,val)
            ret = [val]
    #print(ret)
    return ret

def mappage(request,mapp):
    returnMapp = {}
    for c in mapp:
        try:
            replace = mapp[c]["$replace"]
            mapp[c] = mapp[c]["$path"]
        except:
            replace = ""

        if mapp[c][0] == "$":
            fva = findValueArray(request,mapp[c][1: ])
            if len(fva) > 1:
                returnMapp[c] = fva
            else:
                returnMapp[c] = fva[0] if fva[0] != "" else replace
                
        else:
            returnMapp[c] = mapp[c]
    return(returnMapp)

def update(request,mapped,prefix):
    update = 0

    for r in mapped:
        try:
            if mapped[r] != request['lookup']['propertiesLookup']["["+prefix+"]"+r]:
                update = 1
        except:
            update = 1
    return(update)
def updateLookup(request,reponse,properties):
    print("updateLookup")
    paris = pytz.timezone('Europe/Paris')
    request['properties']['updateTime'] = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
    #request["prefix"] = properties['update']
    id_s = {}
    insertId = [ "task",properties['name'],str(request['properties']['updateTime'])]
    if reponse.get("error"):
        request['properties']["error"] = reponse["error"]
        
    else:
        request['properties']["error"] = "Any"
        
        for ids in reponse:
            if ids != "insertId":
                properties["request"]['id_s'][ids] = reponse[ids]

    for ids in properties["request"]['id_s']:
        if ids != "insertId":
            id_s[ids] = "id_s_"+ids
            request['properties']["id_s_"+ids] = properties["request"]['id_s'][ids]
            insertId.append(ids)
            insertId.append(properties["request"]['id_s'][ids])
        
    
    return {
        "LookUpName": properties["LookUpName"],##properties["LookUpName"]
        "datas": [request['properties']],
        "events": [
            {
                "eventName": "_Task_"+properties["action"]+"_"+properties['name'],
                "eventTime": "updateTime",
                "insertId": insertId
            }
        ],
        "Lookups": [
            {
                "value": "id_s_"+list(id_s.keys())[0],
                "lookup": properties["LookUpName"],
                "id": list(id_s.keys())[0],
                "key": properties["LookUpName"]
            }
        ],
        "ids": id_s,
        "prefix": "_Task_"+properties['name'],
        "properties": "",
        "db": "",
        "source" : ""
    }
def runTask(e):
    retRep = []
    print("startTask")
    url = e["properties"]['url']

    if e["properties"].get("subTime") is None:
        e["properties"]['subTime'] = None
    if e["properties"].get("next") is None:
        e["properties"]['next'] = None
    if e["properties"].get("query") is None:
        e["properties"]['query'] = []
    if e["properties"].get("request") is None:
        e["properties"]['request'] = []
    if e["properties"].get("mapp") is None:
        e["properties"]['mapp'] = {}
    if e["properties"].get("limit") is None:
        e["properties"]['limit'] = 100
    if e["properties"].get("force") is None:
        e["properties"]['limit'] = False
    if e["properties"].get("operation") is None:
        e["properties"]['operation'] = "insert"
    
    requestPayload = {
                "id_s" : {},
                "properties" : {},
                "update" : 1 
            }
    
    if len(e["properties"]['request']) > 0:
        
        
        mapped = mappage(e["properties"]['request'],e["properties"]['mapp'])
        
        if e["properties"]['action'] == "update":
            requestPayload['update'] = update(e["properties"]['request'],mapped,"_Task_"+e["properties"]['name']) 
        requestPayload['properties'] = mapped
        

        for id_s in e["properties"]['request']['id_s']:
            requestPayload['id_s'][id_s] = e["properties"]['request']['id_s'][id_s]
        
    #return(requestPayload)
    payload = json.dumps({
        "subTime": e["properties"]["subTime"],
        "next": e["properties"]["next"],
        "db": e["db"],
        "request" :requestPayload,
        "query" : e["properties"]["query"]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    if requestPayload['update'] == 1:
        
        response = requests.request("POST", url, headers=headers, data=payload)
   
        
        try:
        #print(response.text)
            request = response.json()
        except:
            request = {"error":response.text}
    else:
        request = {"update" : 0}
    if len(requestPayload['properties']) > 0:
        request = updateLookup(requestPayload,request,e["properties"])
    # except:
    #     print("error bizare")
    #     request = {}
    credentials = service_account.Credentials.from_service_account_file(
                './file.json')
        
    publisher = pubsub_v1.PublisherClient(credentials=credentials)
    topic_path = publisher.topic_path("scrapyomama-335508", "trck")
    print("url")  
    print(url)
    print("payload request")
    print(payload) 
    print("reponse_get")
    print(request)  
    request['db'] = e['db']
    request['force'] = e['properties']['force']
    request['source'] = e['properties']['name']
    
    if request.get("datas") is not None:
        #if response.json().get('next') is not None:
        request['compil'] = 1
        retRep.append(json.loads(json.dumps(request, default=str)))
        data = json.dumps(request, default=str)
        data = data.encode("utf-8")
        print(data)
        future = publisher.publish(topic_path, data=data)
        print(future.result())
        print("import.")
        request['datas'] = [request['datas'][0]]
        print("senddata")
        

    rep = {
        "request" : e,
        "message" : "ok",
        "reponse" : request
    }
    
    data = {  
            "name" : "Trigguer",
            "lookup" : "monitor",    
            "properties" :rep,  
            "source" : request['source'] ,
            "db" : request['db'],
            "logs" : 0
            }
    

    if request.get('next') is not None:
        if e["properties"]['limit'] > 0:
            publisher = pubsub_v1.PublisherClient(credentials=credentials)
            topic_path = publisher.topic_path("scrapyomama-335508", "task")
            e["properties"]['limit'] = e["properties"]['limit'] - 1
            e["properties"]['next'] = response.json()["next"]
            print("sendNext")
            print(data) 
            #retRep.append(json.loads(json.dumps(e, default=str)))
            data = json.dumps(e, default=str)
            data = data.encode("utf-8")
            future = publisher.publish(topic_path, data=data)
            print(future.result())
            print("task.")
        
    #sendRunTaskLogs
    return retRep  
    
def main(e):

    
    request_json = e['body']
    try:
      return runTask(request_json)  
    except Exception as e:
      print(str(traceback.format_exc()))
      credentials = service_account.Credentials.from_service_account_file(
          './file.json')

      publisher = pubsub_v1.PublisherClient(credentials=credentials)
      topic_path = publisher.topic_path("scrapyomama-335508", "trck")

      
      rep = {
          "request" : request_json,
          "message" : "error",
          "reponse" : str(traceback.format_exc())
      }
      data = json.dumps({
            "event" : 
            {  
              "name" : "Compil",
              "lookup" : "monitor",    
              "properties" :rep,  
              "source" : request_json['source'] ,
              "db" : request_json['db'],
              "logs" : 0
            }
          })
      # Data must be a bytestring
      data = data.encode("utf-8")
      # When you publish a message, the client returns a future.
      future = publisher.publish(topic_path, data=data)
      return(str(traceback.format_exc()))

