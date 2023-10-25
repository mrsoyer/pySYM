import json 
import jstyleson
import requests
import os
# from dotenv import load_dotenv

def reademploye():
     
     print("listedesemployé")
     return("test")


"""connect to the pipedrive api"""
def connect():
     # load_dotenv()
     PIPEDRIVE_API_KEY = os.getenv("PIPEDRIVE_API_KEY")
     TOKEN = {
          "api_token": PIPEDRIVE_API_KEY
     }
     PIPEDRIVE_BASE_URL = os.getenv("PIPEDRIVE_BASE_URL")
     return TOKEN, PIPEDRIVE_BASE_URL


"""create a new person in pipedrive if not exist"""
def create_person(name, location, address, website, phone):

     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "persons?api_token=" + TOKEN['api_token']

     data = json.dumps({
          "name": name,
          "f529556ddc06ec8ce52f1a2cbe502367921738d1": location,
           "039d8f751c8b4afb601dcb13dd8e0f0a19de6137": address,
          "84f8e17644ad611c0c469925f73c1db534d586be": website,
          "phone": phone
     })
     print(data)
     print(url)
     print(TOKEN)
     headers = {
     'Content-Type': 'application/json',
     'Accept': 'application/json'
     }
     
     response = requests.post(url, data=data, headers=headers)
     return response.json()
     # return {
     #      "data": data,
     #      "url": url,
     #      "TOKEN": TOKEN,
     # }


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