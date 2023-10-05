import pymongo
from pymongo import MongoClient
import certifi
import json
import requests
import os


class symClient:
        def __init__(self, mongo, url,db,ssl = None, workflow = None , trigger= None, var= None, nodes = None, getNode = None, node = None, nodeApp= None, step= None, request= None,collection= None):
                self.mg = str(mongo)       
                if ssl is not None:
                        self.env = "local"

                else:
                         self.env = "prod"
                self.url = url
                self.db = db
                self.ssl = ssl
                if workflow is not None:
                        self.workflow = workflow
                if trigger is not None:
                        self.trigger = trigger
                if var is not None:
                        self.var = var
                if nodes is not None:
                        self.nodes = nodes
                if getNode is not None:
                        self.getNode = getNode
                if node is not None:    
                        self.node = node
                if collection is not None:    
                        self.collection = collection
                if nodeApp is not None:                
                        self.nodeApp = nodeApp
                if step is not None:
                        self.step = step
                if request is not None:
                        self.request = request
        def read(self,val,SYM):
                if isinstance(val, str):
                        if val[0] == "$":
                                val = eval(val[1:])
                return val

        def val(self,SYM):
                if isinstance(SYM.getNode, dict):
                        if SYM.getNode.get('val') is None:
                                pass
                                #SYM.getNode['val'] = 0
                save = 0
                
                if isinstance(SYM.node, str):
                        
                        if SYM.node[0] == "$":
                              
                                SYM.node = eval(SYM.node[1:])
                               
                        else:
                                rep = [{"val" : SYM.node}]
                                save = 1
                elif isinstance(SYM.node, list):
                        rep = SYM.node
                        save = 1
                elif isinstance(SYM.node, dict):
                        rep = [SYM.node]
                        save = 1
                if save == 1:
                        database = "__task_"+SYM.trigger['name']+"_"+SYM.trigger['taskId']
                        collection = str(SYM.trigger['n']).zfill(3)+"_"+SYM.nodeApp+"_"+str(SYM.getNode['val'])
                        SYM.mongo[database][collection].insert_many(rep)
                        SYM.node = SYM.mongo[database][collection]
                        SYM.getNode['val'] += 1
                #return val

        def app(self,controller):
                core = __import__("app."+controller)
                s = getattr(core, "app")
                file = getattr(s, controller)
                
                return(file)

        

        def controller(self,controller):
                
                
                core = __import__("controller."+controller)
                s = getattr(core, "controller")
                file = getattr(s, controller)
                
                return(file)

        def cli(self,request):
                request.pop(0)
                #self.e.pop(0)
                try:
                        controller = request.pop(0)
                except:
                        return ("""Usage: sym [controleur] [--GET_KEY=GET_VALUE] [--data=DATA] [--dataFolder=DATA_FOLDER] [--dataUrl=DATA_URL]] [--help]""")
                request = list(request)
                core = __import__("controller."+controller)
                #s = getattr(core, "controller")
                file = getattr(core, controller)
                Def = getattr(file, "run")
                
                get = {}
                folder = []
                body = {}
                
                for eItem in request:
                        if eItem[:2] == "--":
                                if eItem[2:] == "help":
                                        help = getattr(file, "help")
                                        return help()
                                else:
                                        splitItem = eItem[2:].split("=")
                                        if len(splitItem) == 1:
                                                get[splitItem[0]] = 1
                                        else:
                                                get[splitItem[0]] = splitItem[1]
                        else:
                                folder.append(eItem)
                
                if get.get("data") is not None:
                        body = json.loads(str(get["data"]))
                        #get.pop("data")
                        del get["data"]
                if get.get("dataFolder") is not None:
                        file = open(get['dataFolder'], 'r')
                        body = json.loads(file.read())
                        #get.pop("data")
                        del get["dataFolder"]
                if get.get("dataUrl") is not None:
                        response = requests.request("GET", get['dataUrl'])
                        body = response.json()
                        #get.pop("data")
                        del get["dataUrl"]
                request = {
                        "folder" : folder,
                        "get" : get,
                        "body" : body
                }
                return(Def(request))


      
        def http(self,request):
                #return(self.e.view_args)
                #return(self.e.get_json())
                #self.e.pop(0)
                #self.e.pop(0)
                #
                get = {}
                try:
                        path = request.view_args['path'].split("/")
                except:
                        path = []
                try:
                        body = request.get_json()
                except:
                        body = {}
                try:
                        for args in  request.args:
                                get[args] = request.args.get(args)
                except:
                        get = {}

                controller = path.pop(0)
                core = __import__("controller."+controller)
                #s = getattr(core, "controller")
                file = getattr(core, controller)
                Def = getattr(file, "run")

                request = {
                        "folder" : path,
                        "get" : get,
                        "body" : body
                }
                return(Def(request))




        