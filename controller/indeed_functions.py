"""scrape data from website and return a json file with the results"""
def scrape_offers(request, SYM):
    return SYM.app('indeed').scrape_job_offers(request["folder"][0])


"""run apify to scrape data from website and return a json file with the results"""
def run_apify(request, SYM):
    return SYM.app('indeed').run_apify()


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
            SYM.app('postgre').update_indeed_pipedrive_id("No Phone", company[0])
            continue
        """create a person in pipedrive"""
        if "Marseille" not in company[2]:
            SYM.app('postgre').update_indeed_pipedrive_id("No Marseille", company[0])
        else:
            person = SYM.app('pipedrive').create_person(company[1], company[2], company[3], company[4], company[5])
            person_id = person["data"]["id"]
            """create a lead in pipedrive"""
            indeed_label = "c55790b0-57c8-11ee-86c1-37018efb0033"
            lead = SYM.app('pipedrive').create_lead(company[1], person["data"]["id"], indeed_label)
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
        base_url = "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28W2F4E%29%3B&fromage=1&vjk="
        content = f"<b>Offre:<b> Indeed <br>\
        <b>url:<b> {base_url}{job[0]} <br> \
        <b>Poste:<b> {job[1]} / <b>Entreprise:<b> {job[4]} <br> \
        <b>Effectif(s):<b> {job[3]} <br> \
        <b>Localisation:<b> {job[5]} <br> \
        <b>Salaire:<b> {job[2]} <br> \
        <b>Type de Contrat:<b> {job[3]} <br><br> \
        <b>Description du poste:<b> {job[6]}"

        lead_id = SYM.app('postgre').get_indeed_lead_id(job[7])
        lead_id = lead_id[0][0]
        """create a note in pipedrive"""
        if "Marseille" not in job[5]:
            SYM.app('postgre').update_indeed_note_id("Not Marseille", job[0])
        elif lead_id:
            note = SYM.app('pipedrive').create_note_deal(content, lead_id)
            note_id = note["data"]["id"]
            """update the job offer with the note_id in database"""
            SYM.app('postgre').update_indeed_note_id(note_id, job[0])
            SYM.app('pipedrive').update_lead_metier(lead_id, job[1])
        else:
            SYM.app('postgre').update_indeed_note_id("no lead id", job[0])
    return "done"





#############################################################################################################


"""update company details in the company table from google maps"""
def update_company_v2(request, SYM):
    data = SYM.app('postgre').read_indeed_companies()
    res = []
    for company in data:
        if company[-4] == False:
            company_details = SYM.app('gmaps').get_company_info(company[1], company[2])
            if company_details:
                company_id = company[0]
                company_details["company_id"] = company_id
                res.append(company_details)
            else:
                SYM.app('postgre').update_indeed_company(company[0], "not available", "not available", "not available", "not available", "not available")
                print(company[0], ": not available")
            # try:
            #     SYM.app('postgre').update_indeed_company(company[0], company_details["address"], company_details["website"], company_details["phone"], company_details["lat"], company_details["lng"])
            # except:
            #     pass
    return res



def scrape_job_offers_v2(request, SYM):
    all_job_offers = SYM.app('indeed').scrape_job_offers(request["body"]["defaultDatasetId"])
    for job in all_job_offers:
        postal_code = job["location"].split(" ")[0]
        company_id = str(job["company"] + postal_code).replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
        job["company_id"] = company_id
        if job["companyInfo"]["companyDescription"] == None:
            job["companyInfo"]["companyDescription"] = "No description"

    return all_job_offers