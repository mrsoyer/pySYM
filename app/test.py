import json 
import jstyleson

def run(request,SYM):
     ret = list(request['body']['node']['request'].find({}))
     #js = SYM.app("js")
     
     """js.run({
          "body" : {
          "subTime":1580000000,
          "next" : 100
          },
          "get" :{
          "source":"get-clients-erp",
          }},SYM)"""
     return(ret)
     