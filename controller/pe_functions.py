
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
        print(job)
        # try:
        SYM.app('postgre').insert_job_offer(job["job_title"], job["job_reference"])
        # except:
        #     pass
    return all_job_offers


def update_job_offers(request, SYM):
    data = SYM.app('postgre').read_job_offers()
    for job in data:
        if job[-2] == False:
            print(job)
            job_details = SYM.app('pe').scrape_job_details(job[0])
            print(job_details)
            SYM.app('postgre').update_job_offer(job[0], job_details["company_name"], job_details["company_size"], job_details["company_city"], job_details["company_postal_code"], job_details["company_region"], job_details["company_country"], job_details["description"], job_details["experience"], job_details["skills_list"], job_details["contract_type"], job_details["hours"], job_details["salary"])
            """insert company in its table if it doesn't exist in the table"""
            try:
                SYM.app('postgre').insert_company(job_details["company_name"], job_details["company_postal_code"], job_details["company_city"])
            except:
                pass
    return "done"


"""update company details in the company table from google maps"""
def update_company(request, SYM):
    data = SYM.app('postgre').read_companies()
    print(f"data = {data}")
    for company in data:
        print(f"company = {company}")
        if company[-3] == False:
            company_details = SYM.app('gmaps').get_company_info(company[1], company[2])
            print(f"company_details = {company_details}")
            try:
                SYM.app('postgre').update_company(company[0], company_details["address"], company_details["website"], company_details["phone"], company_details["lat"], company_details["lng"])
            except:
                pass
    return "done"


"""Work flow to create a person in pipedrive if not exist, create a lead and update the company with the pipedrive_id and lead_id in database"""
def wf_1(request, SYM):
    """get companies which have no pipedrive_id from database"""
    data_postgre = SYM.app('postgre').get_companies_with_no_pipedrive_id()

    for company in data_postgre:
        person = SYM.app('pipedrive').create_person(company[1], company[2], company[3], company[4], company[5])
        """get person id from pipedrive"""
        pipedrive_id = person["data"]["id"]
        lead = SYM.app('pipedrive').create_lead(company[1], pipedrive_id)
        lead_id = lead["data"]["id"]
        SYM.app('postgre').update_pipedrive_id(pipedrive_id, company[0])
        SYM.app("postgre").update_lead_id(lead_id, company[0])
    return "done"


"""Work flow to create a note in pipedrive for each job offer which has no note_id in database"""
def wf_2(request, SYM):
    """get job offers which have no note_id from database"""
    data_postgre = SYM.app('postgre').get_job_offers_with_no_note_id()

    for job in data_postgre:
        content = f"<b>Poste:<b> {job[1]} / <b>Entreprise:<b> {job[2]} <br> \
        <b>Effectif(s):<b> {job[3]} <br> \
        <b>Ville:<b> {job[4]} <br> \
            <b>Code Postale:<b> {job[5]} <br> \
                <b>Region:<b> {job[6]} <br> \
                   <b>Pays:<b> {job[7]}  <br><br> \
                        <b>Description:<b> {job[8]} <br> \
                            <b>Experience:<b> {job[9]} <br> \
                                <b>Skills:<b> {job[10]} <br> \
                                    <b>Type de Contrat:<b> {job[11]} <br> \
                                        <b>Horaires:<b> {job[12]} <br> \
                                            <b>Salaire:<b> {job[13]}"
        
        lead_id = SYM.app('postgre').get_lead_id(job[14])
        lead_id = lead_id[0][0]
        deal = SYM.app('pipedrive').create_note_deal(content, lead_id)
        deal_id = deal["data"]["id"]
        SYM.app('postgre').update_note_id(deal_id, job[0])
    return "done"