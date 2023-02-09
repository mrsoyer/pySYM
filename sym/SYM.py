import pymongo
from pymongo import MongoClient
import certifi
import json
import requests
import os


class symClient:
        def __init__(self, mongo, url,db,ssl = None):
                if ssl is not None:
                        self.env = "prod"
                        self.mongo = MongoClient(mongo, tlsCAFile=certifi.where())
                else:
                         self.env = "local"
                         self.mongo = MongoClient(mongo)
                self.url = url
                self.db = db

        def app(self,controller):
                core = __import__("app."+controller)
                file = getattr(core, controller)
                
                return(file)

        def workflow(self,controller):
                core = __import__("workflow."+controller)
                file = getattr(core, controller)
                
                return(file)

        def controller(self,controller):
                
                
                core = __import__("controller."+controller)
                file = getattr(core, controller)
                
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
                return(Def(request,self))


      
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
                file = getattr(core, controller)
                Def = getattr(file, "run")

                request = {
                        "folder" : path,
                        "get" : get,
                        "body" : body
                }
                return(Def(request,self))
        
        def pubSub(self,request):
                get = {}
                try:
                        path = request['folder']
                except:
                        path = []
                try:
                        body = request['body']
                except:
                        body = {}
                try:
                        get = request['get']
                except:
                        get = {}

                controller = path.pop(0)
                core = __import__("controller."+controller)
                file = getattr(core, controller)
                Def = getattr(file, "run")

                request = {
                        "folder" : path,
                        "get" : get,
                        "body" : body
                }
                return(Def(request,self))




        