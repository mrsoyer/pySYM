import json 
import jstyleson
import requests
import os
from dotenv import load_dotenv

def reademploye():
     
     print("listedesemployé")
     return("test")


"""connect to the pipedrive api"""
def connect():
     load_dotenv()
     PIPEDRIVE_API_KEY = os.getenv("PIPEDRIVE_API_KEY")
     TOKEN = {
          "api_token": PIPEDRIVE_API_KEY
     }
     PIPEDRIVE_BASE_URL = os.getenv("PIPEDRIVE_BASE_URL")
     return TOKEN, PIPEDRIVE_BASE_URL


"""create a new person in pipedrive if not exist"""
def create_person(name, city, address, website, phone):

     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "persons"
     data = {
          "name": name,
          # "city": city,
          # "address": address,
          # "website": website,
          "phone": phone
     }
     response = requests.post(url, params=TOKEN, data=data)
     return response.json()


"""create a lead in pipedrive"""
def create_lead(title, person_id):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "leads"
     data = {
          "title": title,
          "person_id": person_id
     }
     response = requests.post(url, params=TOKEN, json=data)
     return response.json()


"""create a note in pipedrive"""
"""content = job offer: title / info: all details of the job offer"""
def create_note_deal(content, lead_id):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "notes"
     data = {
          "content": content,
          "lead_id": lead_id
     }
     response = requests.post(url, params=TOKEN, data=data)
     return response.json()