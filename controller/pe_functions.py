
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
    return SYM.app('pe').scrape_job_details(request["get"]["ref"])

def get_company_info(request, SYM):
    # company_name = "Di Micheli Ristorante"
    # city = "Aix-en-Provence"
    # return request["get"]["company_name"]
    return SYM.app('pe').get_company_info(request["body"]["company_name"], request["body"]["city"])

def get_all_job_titles_and_references(request, SYM):
    # url = "https://candidat.pole-emploi.fr/offres/recherche?domaine=M,D,G,H,M16,K,N&emission=1&lieux=13201&natureOffre=FS,E2&offresPartenaires=false&qualification=0,X&rayon=50&tri=1&typeContrat=CDI,CDD,SAI"
    # return request["get"]["url"]
    return SYM.app('pe').get_all_job_titles_and_references(request["body"]["url"])