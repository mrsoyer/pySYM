"""scrape data from website and return a json file with the results"""
def scrape_offers(request, SYM):
    return SYM.app('indeed').scrape_job_offers(request["folder"][0])


"""run apify to scrape data from website and return a json file with the results"""
def run_apify(request, SYM):
    return SYM.app('indeed').run_apify()

def test(request, SYM):
    return SYM.app('indeed').scrape_job_offers(request["body"]["defaultDatasetId"])

"""save all the job offers in the database"""
def save_all_job_offers_and_companies(request, SYM):
    SYM.app('postgre').connect()
    all_job_offers = SYM.app('indeed').scrape_job_offers(request["body"]["defaultDatasetId"])

    for job in all_job_offers:
        try:
            SYM.app('postgre').insert_indeed_job_offer(job["id"] ,job["positionName"], job["salary"], job["jobType"], job["company"], job["location"], job["description"])
        except:
            pass
        try:
            if job["companyInfo"]["companyDescription"] == None:
                job["companyInfo"]["companyDescription"] = "No description"
            SYM.app('postgre').insert_indeed_company(job["company"], job["location"], job["companyInfo"]["companyDescription"])
        except:
            pass
    return all_job_offers


"""update company details in the company table from google maps"""
def update_company(request, SYM):
    data = SYM.app('postgre').read_indeed_companies()
    for company in data:
        if company[-3] == False:
            company_details = SYM.app('gmaps').get_company_info(company[1], company[2])
            try:
                SYM.app('postgre').update_indeed_company(company[0], company_details["address"], company_details["website"], company_details["phone"], company_details["lat"], company_details["lng"])
            except:
                pass
    return "done"


"""Work flow to create a person in pipedrive if not exist, create a lead and update the company with the pipedrive_id and lead_id in database"""
def wf_1(request, SYM):
    """get companies which have no pipedrive_id from database"""
    data_postgre = SYM.app('postgre').get_indeed_companies_with_no_pipedrive_id()

    for company in data_postgre:
        """check if the company has not a phone number, skip it"""
        if company[5] == "not available":
            continue
        """create a person in pipedrive"""
        person = SYM.app('pipedrive').create_person(company[1], company[2], company[3], company[4], company[5])
        person_id = person["data"]["id"]
        """create a lead in pipedrive"""
        lead = SYM.app('pipedrive').create_lead("job offer", person["data"]["id"])
        lead_id = lead["data"]["id"]
        """update the company with the pipedrive_id and lead_id in database"""
        SYM.app('postgre').update_indeed_pipedrive_id(person_id, company[0])
        SYM.app('postgre').update_indeed_lead_id(lead_id, company[0])
    return "done"


"""Work flow to create a note in pipedrive for each job offer which has no note_id in database"""
def wf_2(request, SYM):
    """get job offers which have no note_id from database"""
    data_postgre = SYM.app('postgre').get_indeed_job_offers_with_no_note_id()

    for job in data_postgre:
        content = f"<b>Poste:<b> {job[1]} / <b>Entreprise:<b> {job[4]} <br> \
        <b>Effectif(s):<b> {job[3]} <br> \
        <b>Localisation:<b> {job[5]} <br> \
        <b>Salaire:<b> {job[2]} <br> \
        <b>Type de Contrat:<b> {job[3]} <br> \
        <b>Description du poste:<b> {job[6]} <br>"
        lead_id = SYM.app('postgre').get_indeed_lead_id(job[7])
        lead_id = lead_id[0][0]
        """create a note in pipedrive"""
        note = SYM.app('pipedrive').create_note_deal(content, lead_id)
        note_id = note["data"]["id"]
        """update the job offer with the note_id in database"""
        SYM.app('postgre').update_indeed_note_id(note_id, job[0])
    return "done"