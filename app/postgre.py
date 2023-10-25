import json 
import jstyleson
import psycopg2
import os


def test():
     
     print("test")
     return("test")


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
     cur.execute("INSERT INTO sym.indeed_job_offer (id , position_name, salary, job_type, company_name, location, description, company_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id ,position_name, salary, jobType, company_name, location, description, company_id))
     conn.commit()
     conn.close()


"""insert company in sym.indeed_company table"""
def insert_indeed_company(name, location, description):
     conn = connect()
     cur = conn.cursor()
     postal_code = location.split(" ")[0]
     company_id = str(name + postal_code).replace(" ", "").replace("'", "").replace("(", "").replace(")", "").replace(".", "").replace(",", "").replace("-", "").replace("_", "")
     cur.execute("INSERT INTO sym.indeed_company (company_id, name, location, description) VALUES (%s, %s, %s, %s)", (company_id, name, location, description))
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