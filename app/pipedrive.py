import json 
import jstyleson
import requests
import os
import random

"""connect to the pipedrive api"""
def connect():
     PIPEDRIVE_API_KEY = os.getenv("PIPEDRIVE_API_KEY")
     TOKEN = {
          "api_token": PIPEDRIVE_API_KEY
     }
     PIPEDRIVE_BASE_URL = os.getenv("PIPEDRIVE_BASE_URL")
     return TOKEN, PIPEDRIVE_BASE_URL


"""create a new person in pipedrive if not exist"""
def create_person(name, location, address, website, phone):

     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "persons"

     data = json.dumps({
          "name": name,
          "f529556ddc06ec8ce52f1a2cbe502367921738d1": location,
           "039d8f751c8b4afb601dcb13dd8e0f0a19de6137": address,
          "84f8e17644ad611c0c469925f73c1db534d586be": website,
          "phone": phone
     })

     headers = {
     'Authorization': f'Bearer {TOKEN["api_token"]}',
     'Content-Type': 'application/json'
     }
     
     response = requests.post(url, data=data, headers=headers, params=TOKEN)
     return response.json()


"""create a lead in pipedrive"""
def create_lead(title, person_id, label_id):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "leads"
     owners_list = [18447689, 18447700]
     owner_id = random.choice(owners_list)
     print("owner_id: ", owner_id)

     data = {
          "title": title,
          "person_id": person_id,
          "owner_id": owner_id,
          "label_ids": [
               label_id
          ]
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


"""get all deals from pipedrive with the field 'cleaned' not equal to 1"""
def get_deals_notCleaned():
    TOKEN, PIPEDRIVE_BASE_URL = connect()
    url = PIPEDRIVE_BASE_URL + "deals"
    params = {
        "api_token": TOKEN["api_token"],
        "filter_id": 88,
        "start": 0,
        "limit": 1,
    }
    response = requests.get(url, params=params)
    deals = response.json()["data"]

    return deals


"""get a deal from pipedrive"""
def get_deal_related_objects(deal_id):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + f"deals/{deal_id}"
     params = {
          "api_token": TOKEN["api_token"],
     }
     response = requests.get(url, params=params)
     deal = response.json()["related_objects"]
     deal_person = deal["person"]
     print(len(deal_person))
     
     return deal


"""update a person in pipedrive"""
def update_person_from_account_business(person_id, data):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + f"persons/{person_id}"
     data = {
          # "name": data[3]+" "+data[4],
          "first_name": data[3],
          "last_name": data[4],
          "email": data[1],
          "fd4d53653d471c62cfe04c155130ab0684644ea6": data[5],
     }
     response = requests.put(url, params=TOKEN, json=data)
     return response.json()


"""update a organization in pipedrive"""
def update_organization_from_account_business(organization_id, data):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + f"organizations/{organization_id}"
     data = {
          "name": data[12],
          "address": data[10] + ", " + data[9] + ", " + data[11],
          "34bb6f62585df8ad42cf3ac70359fe88a15cc404": data[9],
          "address_route": data[10],
          "address_country": "France",
          "address_postal_code": data[11],
          "12f129607fc1ce83773241089fc312f6db4f1281": data[8],
          "ae1e4a5dccbb9e8dd82a6084c6722946d9330a4a": data[13],
          "d97a82c1373c49294be546886a2327432bdfc99a": data[14],
          "phone": data[15],
          "68602f04fa17299e33f2280fcef4f79f77b08875": data[16],
     }
     response = requests.put(url, params=TOKEN, json=data)
     return response.json()

"""update a deal cleaned field in pipedrive"""
def update_deal_cleanedField(deal_id):
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + f"deals/{deal_id}"
     data = {
          "de5b4b741992b57af20863c8da9277f6c18561b6": 1
     }
     response = requests.put(url, params=TOKEN, json=data)
     return response.json()


"""get all deals from pipedrive"""
def get_all_deals():
     TOKEN, PIPEDRIVE_BASE_URL = connect()
     url = PIPEDRIVE_BASE_URL + "deals"
     params = {
          "api_token": TOKEN["api_token"],
          "start": 0
     }
     response = requests.get(url, params=params)
     deals = response.json()["data"]
     return deals