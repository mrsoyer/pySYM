import uuid
import pytz
import datetime
from datetime import  date, timedelta
import json
import traceback
import jstyleson

def parseFolder(request,SYM):
    executeFolder = {
        "insert" : {

        },
        "append" : {

        }
    }
    key = 1
    append=0
    #print(request['folder'])
    if len(request['folder']) > 0:
        request['folder'].insert(0,"webhook")
    for folder in request['folder']:
        if folder == "append":
            append = 1
        elif append == 0:
            if key == 1:
                lastkey = folder
                key = 0
            else:
                executeFolder['insert'][lastkey] = folder
                key = 1
        elif append == 1:
            if key == 1:
                lastkey = folder
                key = 0
            else:
                executeFolder['append'][lastkey] = folder
                append=0
                key = 1

    return(executeFolder)

def workflowfile(execute,fileExe,request,workflow,SYM):
        wfDev = SYM.workflow(fileExe)
        wf =  wfDev.SYM({},SYM)
        try:
            trigger =  wfDev.trigger({},SYM) 
            wf.insert(0,{"$trigger" : trigger}) 
        except:
            print("no trigger")
        i = 0
        if wf[0].get("$trigger") is not None:
            workflow.insert(0, wf[0])
            workflow[0]["$trigger"]['name'] = fileExe
            wf.pop(0)
            i = 1
        if execute == "insert":
            wf.reverse()
            for task in wf:
                workflow.insert(i, task)
        else:
            for task in wf:
                workflow.append(task)
        #request['webhook'] = request['body']
        return i
        
        
def preparWorkflow(executeFolder,workflow,request,SYM):
    i = 0
    wh = 0
    for folder in request['folder']:
        if folder == "webhook":
            wh = 1
    if wh == 0:
        print("no webhook")
        for body in request['body']:
            workflow.append(body)
        if len(workflow) == 0:
            i = i
        elif workflow[0].get("$trigger") is not None:
            i += 1

    for insert in executeFolder['insert']:
        if insert == "webhook":
            i += workflowfile("insert",executeFolder['insert'][insert],request,workflow,SYM)
            #print(request['body'])
            workflow.insert(i,{
                "$webhook" : request['body']
            })
            i += 1
        else:
            workflow.insert(i,{
                "$readCollection" : {
                    "collection" : executeFolder['insert'][insert],
                    "database" : insert,
                }
            })
            i += 1
    for append in executeFolder['append']:
        if append == "webhook":
            workflowfile("append",executeFolder['append'][append],request,workflow,SYM)
        else:
            workflow.append({
                "$readCollection" : {
                    "collection" : executeFolder['append'][append],
                    "database" : append,
                }
            })    
    return(workflow)

def createtrigger(workflow,request,SYM):
    if workflow[0].get("$trigger") is None:
        workflow.insert(0,{
            "$trigger" : request['get']
        }) 
    else:
        for get in request['get']:
            workflow[0]['$trigger'][get] = request['get'][get]

def verifTrigger(trigger,SYM):
    if trigger.get("limit") is  None:
        trigger['limit'] = 100
    if trigger.get("thread") is  None:
        trigger['thread'] = 1
    if trigger.get("offset") is  None:
        trigger['offset'] = 0
    if trigger.get("timeout") is  None:
        trigger['timeout'] = 3600
    if trigger.get("taskId") is  None:
        trigger['taskId'] = str(uuid.uuid4())
    trigger['limit'] = int(trigger['limit'])
    trigger['thread'] = int(trigger['thread'])
    trigger['offset'] = int(trigger['offset'])
    trigger['timeout'] = int(trigger['timeout'])

def startWorkflow(workflow,trigger,request,SYM):
    paris = pytz.timezone('Europe/Paris') 
    trigger['n'] = 0
    
    trigger['create'] = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
    trigger['update'] = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
    #result = workflow[0]
    collection = str(trigger['n']).zfill(3)+"_trigger"
    
    SYM.mongo["___task_"+trigger['name']+"_"+trigger['taskId']][collection].drop()
    
    SYM.mongo["___task_"+trigger['name']+"_"+trigger['taskId']][collection].insert_one(dict(trigger))
    #trigger['n'] += 1

def runNode(database,nodeApp,node,last_query,trigger,workflow,request,SYM):
    app = SYM.app(nodeApp)
    i = 0
    nodes = []
    for w in workflow:
        if i < trigger['n']:
            
            wNodeApp = list(w.keys())[0].replace("$","")
            wNode = w["$"+wNodeApp]
            collection = str(i).zfill(3)+"_"+wNodeApp
            if wNodeApp == "readCollection":
                wQuery = SYM.mongo[SYM.db+"_"+wNode['database']][wNode['collection']]
            else:
                wQuery = SYM.mongo[database][collection]
            nodes.append({
                "get" : wNode,
                "request" : wQuery,
                "app": wNodeApp
            })
            
            i += 1

    body = {
        "trigger" : trigger,
        "workflow" : workflow,
        "nodes" : nodes,
        "node" : {
            "get" : node["$"+nodeApp],
		    "request" : last_query,
		    "app": nodeApp
        }
    }
    try:
        result =  app.run(
            {
                "get" : request['get'],
                "body" : body,
                "folder" : request['folder'],
            },
            SYM
        )
    except:
        error = str(traceback.format_exc()).split("\n")
        #error = traceback.format_exc()
        #error = traceback.format_list(error)
        result = {"error" : error}
        SYM.mongo[SYM.db+"_error"][trigger['name']].insert_one({"workflow":workflow,"trigger":trigger,"result":result})
        trigger['n'] = len(workflow)-1

    return result

def saveResult(result,database,collection,SYM):
    SYM.mongo[database][collection].drop()
    if isinstance(result, list):
        insertResult = []
        for i in result:
            if i.get('_id') is not None:
                del i['_id']
            insertResult.append(i)
            if len(insertResult) == 100:
                SYM.mongo[database][collection].insert_many(insertResult)
                insertResult = []
        if len(insertResult) > 0:
            SYM.mongo[database][collection].insert_many(insertResult)
            insertResult = []
    else:
        if(result.get("async") is None):
            if result.get('_id') is not None:
                del result['_id']
            #print(result)
            SYM.mongo[database][collection].insert_many([dict(result)])

def nextStep(node,current_query,trigger,workflow,database,collection,result,request,SYM):
    if(trigger['n'] == len(workflow)):
        if trigger.get('save') is not None:
            r = current_query.aggregate([
                { "$out": { "coll": trigger['name'], "db": SYM.db+"_SYM" } }
            ])
        trigger['n'] = -1    
        
        trigger['async'] = 1
        r = current_query.find({}).skip(trigger['offset']).limit(trigger['limit'] )
        ret = json.loads(json.dumps({
            "n" : len(workflow)-1,
            "end" : 1,
            "results" : list(r),
            "node" : node,
            "trigger" : trigger,
            "workflow" : workflow
        }, default=str))
        SYM.mongo.drop_database(database)
    else:
        if trigger.get("backgroud") is None:
            controller = SYM.controller("workflow")
            result =  controller.run(
                {
                    "folder" : request['folder'],
                    "get" : request['get'],
                    "body" : workflow,
                },
                SYM
            ) 
            ret = json.loads(json.dumps(result, default=str))
        elif isinstance(result, list):
            SYM.mongo[SYM.db+"_info"]["task"].insert_one({"workflow":workflow,"trigger":trigger})
            trigger['async'] = 0
            #ret = json.loads(json.dumps(workflow, default=str))
        elif result.get("async") is None:
            SYM.mongo[SYM.db+"_info"]["task"].insert_one({"workflow":workflow,"trigger":trigger})
            trigger['async'] = 0
            #ret = json.loads(json.dumps(workflow, default=str))
        else:
            trigger['async'] = 1
            #ret = json.loads(json.dumps(workflow, default=str))
        if trigger.get("backgroud") is not None:
            r = current_query.find({}).skip(trigger['offset']).limit(trigger['limit'] )
            ret = json.loads(json.dumps({
                "n" : trigger['n']-1,
                "results" : list(r),
                "node" : node,
                "trigger" : trigger,
                "workflow" : workflow
            }, default=str))
    return ret

def affichResult(request,SYM):
    if request['get'].get("offset") is None:
        request['get']['offset'] = 0
    if request['get'].get("limit") is None:
        request['get']['limit'] = 500
    if request['get'].get("find") is None:
        request['get']['find'] = {}
    else:
        request['get']['find'] = jstyleson.loads(request['get']['find'])
    request['get']['offset'] = int(request['get']['offset'])  
    request['get']['limit'] = int(request['get']['limit'])
    #print(request['get']['find'])       
    result = SYM.mongo[SYM.db+"_SYM"][request['folder'][0]].find(request['get']['find'] ).skip(request['get']['offset']).limit(request['get']['limit'] )
    return json.loads(json.dumps({"results" : list(result)}, default=str))

def run(request,SYM):
    paris = pytz.timezone('Europe/Paris') 

    workflow = []
    nexist = 0
    if request['get'].get('taskId') is not None:
        now = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
        alltask = SYM.mongo[SYM.db+"_info"]['task'].find({"trigger.taskId" : request['get']['taskId'], "trigger.create" : {"$lt" : now}}).sort("trigger.create", -1).limit(1)
        for task in alltask:
            request['body'] = task['workflow']
            SYM.mongo[SYM.db+"_info"]['task'].delete_one({"_id":task['_id']})

    if isinstance(request['body'], list):
        if len(request['body']) > 0:
            if request['body'][0].get('$trigger') is not None:
               if request['body'][0]['$trigger'].get('n') is not None:    
                    nexist = 1
    if nexist == 0:                
        executeFolder = parseFolder(request,SYM)
        preparWorkflow(executeFolder,workflow,request,SYM)
    else:
        workflow = request['body']

    #return(workflow)
    createtrigger(workflow,request,SYM)
    trigger = workflow[0]['$trigger']
    verifTrigger(trigger,SYM)
    
    if trigger.get("n") is None:
        startWorkflow(workflow,trigger,request,SYM)
    
    
    database = "___task_"+trigger['name']+"_"+str(trigger['taskId']).zfill(3)
    trigger['n'] = int(trigger['n'])
    
    node = workflow[trigger['n']]
    nodeApp = list(node.keys())[0].replace("$","")
    
    #nodeRequest = SYM.mongo[database][last_collection].find({})
    collection = str(trigger['n']).zfill(3)+"_"+nodeApp
    
    if trigger['n'] > 0:
        
        last_node = workflow[trigger['n'] - 1]
        last_nodeApp = list(last_node.keys())[0].replace("$","")
        last_collection = str(trigger['n']-1).zfill(3)+"_"+last_nodeApp
        if last_nodeApp == "readCollection":
            last_query = SYM.mongo[SYM.db+"_"+last_node["$"+last_nodeApp]['database']][last_node["$"+last_nodeApp]['collection']]
        else:
            last_query = SYM.mongo[database][last_collection]
        
        result = runNode(database,nodeApp,node,last_query,trigger,workflow,request,SYM)
        saveResult(result,database,collection,SYM)
        current_query = SYM.mongo[database][collection]
        
    else:
        result=[]
    if nodeApp == "readCollection":
        current_query = SYM.mongo[SYM.db+"_"+node["$"+nodeApp]['database']][node["$"+nodeApp]['collection']]
    else:
        current_query = SYM.mongo[database][collection]
    
        
    
    trigger['n'] += 1
    trigger['update'] = paris.localize(datetime.datetime.utcnow())+ timedelta(hours=2)
    SYM.mongo[database]['000_trigger'].update_many({}, { "$set": trigger })

    ret= nextStep(node,current_query,trigger,workflow,database,collection,result,request,SYM)
    return(ret)