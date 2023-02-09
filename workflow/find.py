def trigger(request,SYM):
    return {
            "name": "workflowTest",
            "async": 0,
            #"result": "1",
            "save": "1",
            "#task": "1",
            "#backgroud": "1",
            "timeout": 3600,
            "limit": 60,
            "thread" : 1,
            #"shedule" : 3600
    }

def SYM(request,SYM):
    return [
        {
            "$py": {"$find" :{}}
        }
        # {
        #     "$test": {
        #         "dataTest": []
        #     }
        # }
    ]
    
def find(request,SYM):
    find = list(request['body']['nodes'][1]['request'].find({}))
    if len(find) > 0:
        find = find[0]
    else:
        find = {"$match": {}}
    if find.get('$limit') is None:
        find['$limit'] = 100
    if find.get('$match') is None:
        find['$match'] = {}

    if find.get('$aggregate') is None:
        find = list(request['body']['node']['request'].find(find['$match']).limit(find['$limit']))
    else:
        find = list(request['body']['node']['request'].aggregate(find['$aggregate']))
    return find