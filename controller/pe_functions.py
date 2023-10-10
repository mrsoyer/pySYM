
def test(request,SYM):
    return request

def scrape_offers(request, SYM):
    # url = "https://candidat.pole-emploi.fr/offres/recherche?domaine=M,D,G,H,M16,K,N&emission=1&lieux=13201&natureOffre=FS,E2&offresPartenaires=false&qualification=0,X&rayon=50&tri=1&typeContrat=CDI,CDD,SAI"
    # return request["get"]["url"]
    # print(request)
    # return SYM.app('pe').test(request["body"]["url"])
    return SYM.app('pe').scrape_job_offers(request["body"]["url"])


def scrape_details(request, SYM):
    # ref = "162XCHZ"
    # return request["get"]["ref"]
    return SYM.app('pe').scrape_job_details(request["folder"][0])


def get_company_info(request, SYM):
    # company_name = "Di Micheli Ristorante"
    # city = "Aix-en-Provence"
    # return request["get"]["company_name"]
    return SYM.app('gmaps').get_company_info(request["body"]["company_name"], request["body"]["city"])


def get_all_job_titles_and_references(request, SYM):
    # url = "https://candidat.pole-emploi.fr/offres/recherche?domaine=M,D,G,H,M16,K,N&emission=1&lieux=13201&natureOffre=FS,E2&offresPartenaires=false&qualification=0,X&rayon=50&tri=1&typeContrat=CDI,CDD,SAI"
    # return request["get"]["url"]
    return SYM.app('pe').get_all_job_titles_and_references(request["body"]["url"])


def save_all_job_offers(request, SYM):
    SYM.app('postgre').connect()
    all_job_offers = SYM.app('pe').get_all_job_titles_and_references(request["body"]["url"])
    for job in all_job_offers["results"]:
        SYM.app('postgre').insert_job_offer(job["job_title"], job["job_reference"])
    return all_job_offers


def update_job_offers(request, SYM):
    data = SYM.app('postgre').read_job_offers()
    for job in data:
        if job[-1] == False:
            job_details = SYM.app('pe').scrape_job_details(job[2])
            SYM.app('postgre').update_job_offer(job[2], job_details["company_name"], job_details["company_size"], job_details["company_city"], job_details["company_postal_code"], job_details["company_region"], job_details["company_country"], job_details["description"], job_details["experience"], job_details["skills_list"], job_details["contract_type"], job_details["hours"], job_details["salary"])
    return "done"


# def save_all_companies(request, SYM):
#     all_job_offers = SYM.app('pe').get_all_job_titles_and_references(request["body"]["url"])
#     for job in all_job_offers["results"]:
#         SYM.app('postgre').insert_company(job["company_name"], job["city"], job["postal_code"])
#     return all_job_offers
    

# def update_company(request, SYM):
#     data = SYM.app('postgre').read_company_table(request["body"]["uniquID"])
#     if data["address"] == None:
#         company_details = SYM.app('gmaps').get_company_info(request["body"]["company_name"], request["body"]["city"])
#         SYM.app('postgre').update_company(request["body"]["uniquID"], company_details["address"], company_details["website"], company_details["phone"], company_details["lat"], company_details["lng"])
#         return company_details
#     else:
#         return "company details already exist"