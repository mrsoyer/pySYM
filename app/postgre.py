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


"""insert job offer in its table"""
def insert_job_offer(title, reference):
     conn = connect()
     cur = conn.cursor()
     cur.execute("INSERT INTO sym.pe_job_offer (title, reference) VALUES (%s, %s)", (title, reference))
     conn.commit()
     conn.close()


"""update job offer with details"""
def update_job_offer(reference, company_name, company_size, company_city, company_postal_code, company_region, company_country, description, experience, skills, contract_type, hours, salary):
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
     """update uniquID = company_name + postal_code"""
     unicID = company_name + company_postal_code
     cur.execute("UPDATE sym.pe_job_offer SET unique_id = %s WHERE reference = %s", (unicID, reference))
     conn.commit()
     conn.close()


"""read pe_job_offer table and return 50 first rows with job_details = false"""
def read_job_offers():
     conn = connect()
     cur = conn.cursor()
     cur.execute("SELECT * FROM sym.pe_job_offer WHERE job_details = false LIMIT 50")
     rows = cur.fetchall()
     conn.close()
     return rows


# """insert company in its table"""
# def insert_company(company_name, city, company_postal_code):
#      conn = connect()
#      cur = conn.cursor()
#      uniquID = company_name + company_postal_code
#      cur.execute("INSERT INTO sym.pe_company (company_name, city, uniquID) VALUES (%s, %s)", (company_name, city, uniquID))
#      conn.commit()
#      conn.close()

# """update company with details"""
# def update_company(uniquID, address, website, phone, lat, lng):
#      conn = connect()
#      cur = conn.cursor()
#      cur.execute("UPDATE sym.pe_company SET address = %s, website = %s, phone = %s, lat = %s, lng = %s WHERE uniquID = %s", (address, website, phone, lat, lng, uniquID))
#      conn.commit()
#      conn.close()


# """read pe_company table and return 50 first rows with company_details = false"""
# def read_companies():
#      conn = connect()
#      cur = conn.cursor()
#      cur.execute("SELECT * FROM sym.pe_company WHERE company_details = false LIMIT 50")
#      rows = cur.fetchall()
#      conn.close()
#      return rows