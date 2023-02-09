import json 
import jstyleson

def run(request,SYM):
     pyfunc = list(request['body']['node']['get'].keys())[0].replace("$","")
     request['body']['py'] = request['body']['node']['get']["$"+pyfunc]

     wfDev = SYM.workflow(request['folder'][0])
     Def = getattr(wfDev, pyfunc)
     wf =  Def(request,SYM)
     
     return(wf)
     