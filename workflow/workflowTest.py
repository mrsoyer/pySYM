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
            "shedule" : 3600
        
    }

def SYM(request,SYM):
    return [
        {
            "$js": {
                "source": "get-clients-erp"
            }
        },
        {
            "$py": {"$test" : "test"}
        }
        # {
        #     "$test": {
        #         "dataTest": []
        #     }
        # }
    ]

def test(request,SYM):
    result = list(request['body']['node']['request'].find({}))
    result = result[0]['datas']
    return result