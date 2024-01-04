# def scraping(request, SYM):
#     return SYM.app('meteojob').scrape_job_offers(request["body"]["url"])


"""update company details in the company table from google maps with lat and lng"""
def update_company_with_lat_lng(request, SYM):
    data = SYM.app('postgre').read_meteojob_companies()
    print(data)
    res = []
    for company in data:
        if company[-3] == False:
            company_details = SYM.app('gmaps').get_company_info_with_name_lat_lng(company[2], company[8], company[9])
            if company_details:
                company_id = company[0]
                company_details["company_id"] = company_id
                res.append(company_details)
                print(company_details)
            else:
                SYM.app('postgre').update_meteojob_company(company[0], "not available", "not available", "not available")
    return res