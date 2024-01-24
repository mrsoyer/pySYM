import difflib

def rate_location(request, SYM):
    rate = SYM.app('rating').rate_location(request["body"]["location"])
    return rate

def rate_title(request, SYM):
    db = SYM.app('postgre').check_job_title(request["body"]["title"])
    if db:
        return db[0][0]
    else:
        return 0
    

def rate_lead(request, SYM):
    rate_loc = SYM.app('rating').rate_location(request["body"]["location"])
    job_names = SYM.app('postgre').get_all_trade_name()
    list_job_names = []
    for job_name in job_names:
        list_job_names.append(job_name[0])
    print(list_job_names)

    job_title = request["body"]["title"]
    print(job_title)

    """check if job_title totally match or partially match with list_job_names"""
    if difflib.get_close_matches(job_title, list_job_names, cutoff=0.5):
        job_title = difflib.get_close_matches(job_title, list_job_names, cutoff=0.5)[0]
        rate_name = 5
    else:
        job_title = "Not Found in Database"
        rate_name = 1


    rate = rate_loc + rate_name
    print(rate)
    upd = SYM.app('pipedrive').update_lead_rate(request["body"]["lead_id"], rate)
    return {"rate": rate, "job_names": list_job_names, "job_title": job_title}