import datetime
from datetime import timedelta
import os
import jstyleson
import pytz
from google.cloud import pubsub_v1
from google.oauth2 import service_account

def cleanLastTask(now,SYM):
    
    expireTask = SYM.mongo[SYM.db+"_info"]['task'].aggregate([
        {
            "$match":
                {
                "$expr":
                    {
                        "$lt":
                            [
                            "$trigger.create",
                                {
                                "$dateSubtract":
                                    {
                                        "startDate": now,
                                        "unit": "second",
                                        "amount": "$trigger.timeout"
                                    }
                                }
                            ]
                    }
                }
        },
        {
            "$project": {
                "_id": 1,
            }
        }
        
    ])
    for task in expireTask:
        SYM.mongo[SYM.db+"_info"]['task'].delete_one({"_id":task['_id']})
    
    dbs = SYM.mongo.list_database_names()
    for db in dbs:
        if db[:7] == "___task":
            count = SYM.mongo[db]['000_trigger'].count_documents({})
            if count > 0:
                count = SYM.mongo[db]['000_trigger'].aggregate([
                    {
                        "$match":
                            {
                            "$expr":
                                {
                                    "$gt":
                                        [
                                        "$create",
                                            {
                                            "$dateSubtract":
                                                {
                                                    "startDate": now,
                                                    "unit": "second",
                                                    "amount": "$timeout"
                                                }
                                            }
                                        ]
                                }
                            }
                    },
                    {
                       "$count": "count"
                    }
                ])
                count = list(count)[0]['count']
                
            if count == 0:
                #print("drop database "+db)
                SYM.mongo.drop_database(db)
def shedule(now,SYM):
    paris = pytz.timezone('Europe/Paris') 
    now = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
    for Workflow1  in os.listdir('./workflow'):
        if(Workflow1.find(".py") == -1):
            continue
        try:
            wfDev = SYM.workflow(Workflow1.replace(".py", ""))
            trigger =  wfDev.trigger({},SYM) 
            wj =  wfDev.SYM({},SYM) 
            wj.insert(0,{"$trigger" : trigger})
        except:
            continue
        if  trigger.get('shedule') is not None:
            trigger['shedule'] = int(trigger['shedule'])
            
            task = SYM.mongo[SYM.db+"_info"]['task'].count_documents(
                {
                    "trigger.name":Workflow1.replace(".py", ""),
                    "trigger.create" : {"$gt" : now  }
                })
            if task == 0:
                trigger['create'] = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2) + timedelta(seconds=trigger['shedule'])
                trigger['update'] = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2) + timedelta(seconds=trigger['shedule'])
                
                SYM.mongo[SYM.db+"_info"]["task"].insert_one({"workflow":wj,"trigger":trigger})

def executeTask(now,SYM):
    
    limitTotal = int(os.getenv('LIMIT')) - SYM.mongo[SYM.db+"_info"]['task'].count_documents({"run":1})
    limitTask = {}
    if limitTotal > 10:
        limitFind = 10
    else:
        limitFind = limitTotal
    alltask = SYM.mongo[SYM.db+"_info"]['task'].find({"trigger.create" : {"$lt" : now}}).limit(limitFind)
    execute = 0
    controller = SYM.controller("workflow")
    for task in alltask:
        if limitTask.get(task['trigger']['name']) is None:
            limitTask[task['trigger']['name']] = task['trigger']['thread']
        
        if limitTask[task['trigger']['name']] > 0 and limitTotal > 0:
            SYM.mongo[SYM.db+"_info"]['task'].update_one({"_id":task['_id']},{"$set":{"run":1}})
            
            result =  controller.run(
                {
                    "folder" : [],
                    "get" : [],
                    "body" : task['workflow'],
                },
                SYM
            ) 
            SYM.mongo[SYM.db+"_info"]['task'].delete_one({"_id":task['_id']})
            limitTask[task['trigger']['name']] -= 1
            limitTotal -= 1
            execute += 1
    if execute == 0:
        return 0
    else:
        return limitTotal

def run(request,SYM):
    paris = pytz.timezone('Europe/Paris') 
    now = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
    #now = datetime.now()
    cleanLastTask(now,SYM)
    shedule(now,SYM)
    run = executeTask(now,SYM)
    if run > 0:
        if SYM.env == "local":
            controller = SYM.controller("runWorkflow")
            result =  controller.run(
                {
                    "folder" : [],
                    "get" : [],
                    "body" : [],
                },
                SYM
            )
        else:
            publisher = pubsub_v1.PublisherClient(credentials=credentials)
            topic_path = publisher.topic_path("scrapyomama-335508", "task")
            data = json.dumps({
                    "folder" : ["runWorkflow"],
                    "get" : [],
                    "body" : [],
                }, default=str)
            data = data.encode("utf-8")
            future = publisher.publish(topic_path, data=data)
            #print(future.result())
    
    return ([])
