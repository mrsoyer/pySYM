import json 
import jstyleson
import psycopg2
import os
from datetime import datetime


"""connect to the postgre database"""
def connect():
     DB_URL = os.getenv("DATABASE_URL")
     conn = psycopg2.connect(DB_URL, sslmode='require')
     return conn


# FOLLOWING FUNCTIONS ARE FOR PE JOB OFFERS AND COMPANIES (PE = Pôle Emploi, l.22-167)
"""insert job offer in sym.pe_job_offer table"""
def insert_pe_job_offer(title, reference):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.pe_job_offer (title, reference) VALUES (%s, %s)", (title, reference))
     conn.commit()
     conn.close()


"""update job offer with details in sym.pe_job_offer table"""
def update_pe_job_offer(reference, company_name, company_size, company_city, company_postal_code, company_region, company_country, description, experience, skills, contract_type, hours, salary):
     conn = connect()
     cur = conn.cursor()
     if company_name == None or company_postal_code == None:
          conn.close()
          return "company name or postal code is missing"
     cur.execute("UPDATE sym.pe_job_offer \
                 SET company_name = %s, company_size = %s, company_city = %s, company_postal_code = %s, \
                 company_region = %s, company_country = %s, description = %s, experience = %s, skills = %s, \
                 contract_type = %s, hours = %s, salary = %s WHERE reference = %s", \
                    (company_name, company_size, company_city, company_postal_code, company_region, company_country, description, experience, skills, contract_type, hours, salary, reference))
     """turn job_details bool to true"""
     cur.execute("UPDATE sym.pe_job_offer SET job_details = true WHERE reference = %s", (reference,))
     company_id = str(company_name + company_postal_code).replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
     cur.execute("UPDATE sym.pe_job_offer SET company_id = %s WHERE reference = %s", (company_id, reference))
     conn.commit()
     conn.close()


"""read pe_job_offer table and return 50 first rows with job_details = false"""
def read_pe_job_offers():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.pe_job_offer WHERE job_details = false LIMIT 50")
     rows = cur.fetchall()
     conn.close()
     return rows


"""insert company in sym.pe_company table"""
def insert_pe_company(name, postal_code, city):
     conn = connect()
     cur = conn.cursor()
     if name == None or postal_code == None:
          conn.close()
          return "company name or postal code is missing"
     company_id = str(name + postal_code).replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
     cur.execute("INSERT INTO sym.pe_company (company_id, name, city) VALUES (%s, %s, %s)", (company_id, name, city))
     conn.commit()
     conn.close()


"""update company with details in sym.pe_company table"""
def update_pe_company(company_id, address, website, phone, lat, lng):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.pe_company SET address = %s, website = %s, phone = %s, lat = %s, lng = %s WHERE company_id = %s", (address, website, phone, lat, lng, company_id))
     """turn company_details bool to true"""
     cur.execute("UPDATE sym.pe_company SET company_details = true WHERE company_id = %s", (company_id,))
     conn.commit()
     conn.close()


"""read pe_company table and return 50 first rows with company_details = false"""
def read_pe_companies():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.pe_company WHERE company_details = false LIMIT 50")
     rows = cur.fetchall()
     conn.close()
     return rows


"""from pe_company table, remove all companies with company_details = false"""
def delete_pe_companies():
     conn = connect()
     cur = conn.cursor()
     cur.execute("DELETE FROM sym.pe_company WHERE company_details = false")
     conn.commit()
     conn.close()


"""get all companies from pe_company table"""
def get_all_pe_companies():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.pe_company")
     rows = cur.fetchall()
     conn.close()
     return rows


"""get all companies which have no pipedrive_id and company_details = true from pe_company table"""
def get_pe_companies_with_no_pipedrive_id():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.pe_company WHERE pipedrive_id IS NULL AND company_details = true LIMIT 10")
     rows = cur.fetchall()
     conn.close()
     return rows


"""get all job offers which have no note_id in pe_job_offer table and its company has a pipedrive_id in pe_company table"""
def get_pe_job_offers_with_no_note_id():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.pe_job_offer WHERE note_id IS NULL AND company_id IN (SELECT company_id FROM sym.pe_company WHERE pipedrive_id IS NOT NULL) LIMIT 10")
     rows = cur.fetchall()
     conn.close()
     return rows


"""update pipedrive_id in pe_company table"""
def update_pe_pipedrive_id(pipedrive_id, company_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.pe_company SET pipedrive_id = %s WHERE company_id = %s", (pipedrive_id, company_id))
     conn.commit()
     conn.close()


"""update lead_id in pe_company table"""
def update_pe_lead_id(lead_id, company_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.pe_company SET lead_id = %s WHERE company_id = %s", (lead_id, company_id))
     conn.commit()
     conn.close()


"""update note_id in pe_job_offer table"""
def update_pe_note_id(note_id, reference):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.pe_job_offer SET note_id = %s WHERE reference = %s", (note_id, reference))
     conn.commit()
     conn.close()


"""get lead_id in pe_company from company_id"""
def get_pe_lead_id(company_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT lead_id FROM sym.pe_company WHERE company_id = %s", (company_id,))
     rows = cur.fetchall()
     conn.close()
     return rows



# FOLLOWING FUNCTIONS ARE FOR INDEED JOB OFFERS AND COMPANIES (l.173-267)
"""insert job offer in sym.indeed_job_offer table"""
def insert_indeed_job_offer(id ,position_name, salary, jobType, company_name, location, description):
     conn = connect()
     cur = conn.cursor()
     postal_code = location.split(" ")[0]
     company_id = str(company_name + postal_code).replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
     """get current time"""
     now = datetime.now()
     formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
     cur.execute("INSERT INTO sym.indeed_job_offer (id , position_name, salary, job_type, company_name, location, description, company_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (id ,position_name, salary, jobType, company_name, location, description, company_id, formatted_date))
     conn.commit()
     conn.close()


"""insert company in sym.indeed_company table"""
def insert_indeed_company(name, location, description):
     conn = connect()
     cur = conn.cursor()
     postal_code = location.split(" ")[0]
     company_id = str(name + postal_code).replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
     """get current time"""
     now = datetime.now()
     formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
     cur.execute("INSERT INTO sym.indeed_company (company_id, name, location, description, created_at) VALUES (%s, %s, %s, %s, %s)", (company_id, name, location, description, formatted_date))
     conn.commit()
     conn.close()


"""read indeed company table and return 50 first rows with company_details = false"""
def read_indeed_companies():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.indeed_company WHERE company_details = false LIMIT 50")
     rows = cur.fetchall()
     conn.close()
     return rows


"""update company with details in sym.indeed_company table"""
def update_indeed_company(company_id, address, website, phone, lat, lng):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.indeed_company SET address = %s, website = %s, phone = %s, lat = %s, lng = %s WHERE company_id = %s", (address, website, phone, lat, lng, company_id))
     """turn company_details bool to true"""
     cur.execute("UPDATE sym.indeed_company SET company_details = true WHERE company_id = %s", (company_id,))
     conn.commit()
     conn.close()


"""get all companies which have no pipedrive_id and company_details = true from indeed_company table"""
def get_indeed_companies_with_no_pipedrive_id():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.indeed_company WHERE pipedrive_id IS NULL AND company_details = true LIMIT 10")
     rows = cur.fetchall()
     conn.close()
     return rows


"""update lead_id in indeed_company table"""
def update_indeed_lead_id(lead_id, company_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.indeed_company SET lead_id = %s WHERE company_id = %s", (lead_id, company_id))
     conn.commit()
     conn.close()


"""get lead_id in indeed_company from company_id"""
def get_indeed_lead_id(company_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT lead_id FROM sym.indeed_company WHERE company_id = %s", (company_id,))
     rows = cur.fetchall()
     conn.close()
     return rows


"""update pipedrive_id in indeed_company table"""
def update_indeed_pipedrive_id(pipedrive_id, company_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.indeed_company SET pipedrive_id = %s WHERE company_id = %s", (pipedrive_id, company_id))
     conn.commit()
     conn.close()


"""update note_id in indeed_job_offer table"""
def update_indeed_note_id(note_id, id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.indeed_job_offer SET note_id = %s WHERE id = %s", (note_id, id))
     conn.commit()
     conn.close()


"""get all job offers which have no note_id in indeed_job_offer table and its company has a pipedrive_id in indeed_company table"""
def get_indeed_job_offers_with_no_note_id():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.indeed_job_offer WHERE note_id IS NULL AND company_id IN (SELECT company_id FROM sym.indeed_company WHERE pipedrive_id IS NOT NULL) LIMIT 10")
     rows = cur.fetchall()
     conn.close()
     return rows


# FOLLOWING FUNCTIONS ARE FOR LINK TABLES, DONT_FIND AND PROBLEM TABLES (l.268-384)
"""read Account table join with Business table"""
def read_account_business():
     conn = connect()
     cur = conn.cursor()
     cur.execute('SELECT public."Account".id, public."Account".email, public."Account"."createdAt" , public."Account"."firstName", public."Account"."lastName", public."Account".gender, public."Business".id, public."Business"."createdAt", public."Business".siret, public."Business"."addressCity", public."Business"."addressStreet", public."Business"."addressZipCode", public."Business"."companyName", public."Business".description, public."Business".function, public."Business".phone, public."Business"."businessType", public."Business"."pipedrivePersonId" \
          FROM public."Account" JOIN public."Business" ON public."Account".id = public."Business"."accountId"')
     rows = cur.fetchall()
     conn.close()
     return rows


"""select and read Account table join with Business table row where pipedrivePersonId = pipedrivePersonID"""
def read_account_business_from_pipedriveID(pipedrivePersonID):
     conn = connect()
     cur = conn.cursor()
     cur.execute('SELECT public."Account".id, public."Account".email, public."Account"."createdAt" , public."Account"."firstName", public."Account"."lastName", public."Account".gender, public."Business".id, public."Business"."createdAt", public."Business".siret, public."Business"."addressCity", public."Business"."addressStreet", public."Business"."addressZipCode", public."Business"."companyName", public."Business".description, public."Business".function, public."Business".phone, public."Business"."businessType", public."Business"."pipedrivePersonId" \
          FROM public."Account" JOIN public."Business" ON public."Account".id = public."Business"."accountId"\
          WHERE public."Business"."pipedrivePersonId" = %s', (str(pipedrivePersonID),))
     rows = cur.fetchall()
     conn.close()
     return rows


"""select and read Account table join with Business table row where email = email"""
def read_account_business_from_email(email):
     conn = connect()
     cur = conn.cursor()
     cur.execute('SELECT public."Account".id, public."Account".email, public."Account"."createdAt" , public."Account"."firstName", public."Account"."lastName", public."Account".gender, public."Business".id, public."Business"."createdAt", public."Business".siret, public."Business"."addressCity", public."Business"."addressStreet", public."Business"."addressZipCode", public."Business"."companyName", public."Business".description, public."Business".function, public."Business".phone, public."Business"."businessType", public."Business"."pipedrivePersonId" \
          FROM public."Account" JOIN public."Business" ON public."Account".id = public."Business"."accountId"\
          WHERE public."Account".email = %s', (str(email),))
     rows = cur.fetchall()
     conn.close()
     return rows


"""select and read Account table join with Business table row where phone = phone"""
def read_account_business_from_phone(phone):
     conn = connect()
     cur = conn.cursor()
     cur.execute('SELECT public."Account".id, public."Account".email, public."Account"."createdAt" , public."Account"."firstName", public."Account"."lastName", public."Account".gender, public."Business".id, public."Business"."createdAt", public."Business".siret, public."Business"."addressCity", public."Business"."addressStreet", public."Business"."addressZipCode", public."Business"."companyName", public."Business".description, public."Business".function, public."Business".phone, public."Business"."businessType", public."Business"."pipedrivePersonId" \
          FROM public."Account" JOIN public."Business" ON public."Account".id = public."Business"."accountId"\
          WHERE public."Business".phone = %s', (str(phone),))
     rows = cur.fetchall()
     conn.close()
     return rows


"""insert deal id in dont_find table"""
def insert_dont_find_deal_id(deal_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.dont_find (deal_id) VALUES (%s)", (deal_id,))
     conn.commit()
     conn.close()


"""insert deal id in problem table"""
def insert_problem_deal_id(deal_id, problem):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.problem (deal_id, description) VALUES (%s, %s)", (deal_id, problem))
     conn.commit()
     conn.close()


"""insert account id and pipedrive id in link account_person table"""
def insert_link_account(account_id, pipedrive_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.link_account_person (account_id, pipedrive_id) VALUES (%s, %s)", (account_id, pipedrive_id))
     conn.commit()
     conn.close()


"""insert business id and pipedrive id in link business_company table"""
def insert_link_business(business_id, pipedrive_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.link_business_company (business_id, pipedrive_id) VALUES (%s, %s)", (business_id, pipedrive_id))
     conn.commit()
     conn.close()


"""insert business id, deal id and pipeline name in link business_deal table"""
def insert_link_business_deal(business_id, deal_id, pipeline_name):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.link_business_deal (business_id, deal_id, pipeline_name) VALUES (%s, %s, %s)", (business_id, deal_id, pipeline_name))
     conn.commit()
     conn.close()


"""read link business_deal table from deal_id"""
def read_link_business_deal(deal_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.link_business_deal WHERE deal_id = '%s'", (deal_id,))
     rows = cur.fetchall()
     conn.close()
     return rows


"""read link business_deal table from business_id"""
def read_link_business_deal_from_business_id(business_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.link_business_deal WHERE business_id = %s", (business_id,))
     rows = cur.fetchall()
     conn.close()
     return rows


"""update link business_deal table with deal_id"""
def update_link_business_deal(business_id, new_deal_id, new_pipeline_name):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.link_business_deal SET deal_id = '%s', pipeline_name = %s WHERE business_id = %s", (new_deal_id, new_pipeline_name, business_id))
     conn.commit()
     conn.close()


"""remove link business_deal table from deal_id"""
def remove_link_business_deal(deal_id):
     conn = connect()
     cur = conn.cursor()
     cur.execute("DELETE FROM sym.link_business_deal WHERE deal_id = %s", (deal_id,))
     conn.commit()
     conn.close()


"""read meteojob_company table and return 50 first rows with company_details = false"""
def read_meteojob_companies():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.meteojob_company WHERE company_details = false LIMIT 50")
     rows = cur.fetchall()
     conn.close()
     return rows


"""update company with details in sym.meteojob_company table"""
def update_meteojob_company(company_id, address, website, phone):
     conn = connect()
     cur = conn.cursor()
     cur.execute("UPDATE sym.meteojob_company SET address = %s, website = %s, phone = %s WHERE company_id = %s", (address, website, phone, company_id))
     """turn company_details bool to true"""
     cur.execute("UPDATE sym.meteojob_company SET company_details = true WHERE company_id = %s", (company_id,))
     conn.commit()
     conn.close()