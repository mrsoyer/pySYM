
def test(request,SYM):
    return request

def scrape_offers(request, SYM):
    # url = "https://candidat.pole-emploi.fr/offres/recherche?domaine=M,D,G,H,M16,K,N&emission=1&lieux=13201&natureOffre=FS,E2&offresPartenaires=false&qualification=0,X&rayon=50&tri=1&typeContrat=CDI,CDD,SAI"
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
        try:
            SYM.app('postgre').insert_pe_job_offer(job["job_title"], job["job_reference"])
        except:
            pass
    return all_job_offers


def update_job_offers(request, SYM):
    data = SYM.app('postgre').read_pe_job_offers()
    for job in data:
        if job[-2] == False:
            job_details = SYM.app('pe').scrape_job_details(job[0])
            try:
                SYM.app('postgre').update_pe_job_offer(job[0], job_details["company_name"], job_details["company_size"], job_details["company_city"], job_details["company_postal_code"], job_details["company_region"], job_details["company_country"], job_details["description"], job_details["experience"], job_details["skills_list"], job_details["contract_type"], job_details["hours"], job_details["salary"])
            except:
                pass
            """insert company in its table if it doesn't exist in the table"""
            try:
                SYM.app('postgre').insert_pe_company(job_details["company_name"], job_details["company_postal_code"], job_details["company_city"])
            except:
                pass
    return "done"


"""update company details in the company table from google maps"""
def update_company(request, SYM):
    data = SYM.app('postgre').read_pe_companies()
    for company in data:
        if company[-3] == False:
            company_details = SYM.app('gmaps').get_company_info(company[1], company[2])
            try:
                SYM.app('postgre').update_pe_company(company[0], company_details["address"], company_details["website"], company_details["phone"], company_details["lat"], company_details["lng"])
            except:
                pass
    return "done"


"""Work flow to create a person in pipedrive if not exist, create a lead and update the company with the pipedrive_id and lead_id in database"""
def wf_1(request, SYM):
    """get companies which have no pipedrive_id from database"""
    data_postgre = SYM.app('postgre').get_pe_companies_with_no_pipedrive_id()

    for company in data_postgre:
        """check if the company has not a phone number, skip it"""
        if company[5] == "not available":
            SYM.app('postgre').update_pe_pipedrive_id("No Phone", company[0])
            continue
        if "Marseille" not in company[2]:
            SYM.app('postgre').update_pe_pipedrive_id("No Marseille", company[0])
        else:
            """create person in pipedrive"""
            person = SYM.app('pipedrive').create_person(company[1], company[2], company[3], company[4], company[5])
            """get person id from pipedrive"""
            pipedrive_id = person["data"]["id"]
            """create a lead in pipedrive"""
            pe_label = "8f7d64b0-57b9-11ee-9d7c-b375ab877442"
            lead = SYM.app('pipedrive').create_lead(company[1], pipedrive_id, pe_label)
            lead_id = lead["data"]["id"]
            SYM.app('postgre').update_pe_pipedrive_id(pipedrive_id, company[0])
            SYM.app("postgre").update_pe_lead_id(lead_id, company[0])
    return "done"


"""Work flow to create a note in pipedrive for each job offer which has no note_id in database"""
def wf_2(request, SYM):
    """get job offers which have no note_id from database"""
    data_postgre = SYM.app('postgre').get_pe_job_offers_with_no_note_id()

    for job in data_postgre:
        content = f"<b>Offre:<b> Pole Emploi <br>\
        <b>url:<b> https://candidat.pole-emploi.fr/offres/recherche/detail/{job[0]} <br> \
        <b>Poste:<b> {job[1]} / <b>Entreprise:<b> {job[2]} <br> \
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
        
        lead_id = SYM.app('postgre').get_pe_lead_id(job[14])
        lead_id = lead_id[0][0]
        """create a note in pipedrive"""
        if "Marseille" not in job[4]:
            SYM.app('postgre').update_pe_note_id("Not Marseille", job[0])
        elif lead_id:
            note = SYM.app('pipedrive').create_note_deal(content, lead_id)
            note_id = note["data"]["id"]
            SYM.app('postgre').update_pe_note_id(note_id, job[0])
            SYM.app('pipedrive').update_lead_metier(lead_id, job[1])
        else:
            SYM.app('postgre').update_pe_note_id("no lead id", job[0])
    return "done"







####################################################################################


def scrape_job_titles_and_references(request, SYM):
    SYM.app('postgre').connect()
    all_job_offers = SYM.app('pe').get_all_job_titles_and_references(request["body"]["url"])

    # for job in all_job_offers["results"]:
    #     try:
    #         SYM.app('postgre').insert_pe_job_offer(job["job_title"], job["job_reference"])
    #     except:
    #         pass
    return all_job_offers


def update_job_offers_v2(request, SYM):
    data = SYM.app('postgre').read_pe_job_offers()
    res = []
    for job in data:
        if job[-3] == False:
            job_details = SYM.app('pe').scrape_job_details(job[0])
            company_id = str(job_details["company_name"]) + str(job_details["company_postal_code"])
            company_id = company_id.replace(" ", "").replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
            job_details["company_id"] = company_id
            print(job_details)
            res.append(job_details)
            break

            # try:
            #     SYM.app('postgre').update_pe_job_offer(job[0], job_details["company_name"], job_details["company_size"], job_details["company_city"], job_details["company_postal_code"], job_details["company_region"], job_details["company_country"], job_details["description"], job_details["experience"], job_details["skills_list"], job_details["contract_type"], job_details["hours"], job_details["salary"])
            # except:
            #     pass
            # """insert company in its table if it doesn't exist in the table"""
            # try:
            #     SYM.app('postgre').insert_pe_company(job_details["company_name"], job_details["company_postal_code"], job_details["company_city"])
            # except:
            #     pass
    return res


def update_company_v2(request, SYM):
    data = SYM.app('postgre').read_pe_companies()
    res = []
    for company in data:
        if company[-4] == False:
            company_details = SYM.app('gmaps').get_company_info(company[1], company[2])
            res.append(company_details)
            # try:
            #     SYM.app('postgre').update_pe_company(company[0], company_details["address"], company_details["website"], company_details["phone"], company_details["lat"], company_details["lng"])
            # except:
            #     pass
    return res


"""Work flow to create a person in pipedrive if not exist, create a lead and update the company with the pipedrive_id and lead_id in database"""
def wf_1_v2(request, SYM):
    """get companies which have no pipedrive_id from database"""
    data_postgre = SYM.app('postgre').get_pe_companies_with_no_pipedrive_id()

    # for company in data_postgre:
    #     """check if the company has not a phone number, skip it"""
    #     if company[5] == "not available":
    #         SYM.app('postgre').update_pe_pipedrive_id("No Phone", company[0])
    #         continue
    #     if "Marseille" not in company[2]:
    #         SYM.app('postgre').update_pe_pipedrive_id("No Marseille", company[0])
    #     else:
    #         """create person in pipedrive"""
    #         person = SYM.app('pipedrive').create_person(company[1], company[2], company[3], company[4], company[5])
    #         """get person id from pipedrive"""
    #         pipedrive_id = person["data"]["id"]
    #         """create a lead in pipedrive"""
    #         pe_label = "8f7d64b0-57b9-11ee-9d7c-b375ab877442"
    #         lead = SYM.app('pipedrive').create_lead(company[1], pipedrive_id, pe_label)
    #         lead_id = lead["data"]["id"]
    #         SYM.app('postgre').update_pe_pipedrive_id(pipedrive_id, company[0])
    #         SYM.app("postgre").update_pe_lead_id(lead_id, company[0])

    return data_postgre


"""Work flow to create a note in pipedrive for each job offer which has no note_id in database"""
def wf_2_v2(request, SYM):
    """get job offers which have no note_id from database"""
    data_postgre = SYM.app('postgre').get_pe_job_offers_with_no_note_id()

    # for job in data_postgre:
    #     content = f"<b>Offre:<b> Pole Emploi <br>\
    #     <b>url:<b> https://candidat.pole-emploi.fr/offres/recherche/detail/{job[0]} <br> \
    #     <b>Poste:<b> {job[1]} / <b>Entreprise:<b> {job[2]} <br> \
    #     <b>Effectif(s):<b> {job[3]} <br> \
    #     <b>Ville:<b> {job[4]} <br> \
    #     <b>Code Postale:<b> {job[5]} <br> \
    #     <b>Region:<b> {job[6]} <br> \
    #     <b>Pays:<b> {job[7]}  <br><br> \
    #     <b>Description:<b> {job[8]} <br> \
    #     <b>Experience:<b> {job[9]} <br> \
    #     <b>Skills:<b> {job[10]} <br> \
    #     <b>Type de Contrat:<b> {job[11]} <br> \
    #     <b>Horaires:<b> {job[12]} <br> \
    #     <b>Salaire:<b> {job[13]}"
        
    #     lead_id = SYM.app('postgre').get_pe_lead_id(job[14])
    #     lead_id = lead_id[0][0]
    #     """create a note in pipedrive"""
    #     if "Marseille" not in job[4]:
    #         SYM.app('postgre').update_pe_note_id("Not Marseille", job[0])
    #     elif lead_id:
    #         note = SYM.app('pipedrive').create_note_deal(content, lead_id)
    #         note_id = note["data"]["id"]
    #         SYM.app('postgre').update_pe_note_id(note_id, job[0])
    #         SYM.app('pipedrive').update_lead_metier(lead_id, job[1])
    #     else:
    #         SYM.app('postgre').update_pe_note_id("no lead id", job[0])
    return data_postgre