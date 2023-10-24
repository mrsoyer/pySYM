import requests
import json
import os


# APIFY_BASE_URL = os.getenv("APIFY_BASE_URL")

def test():
  APIFY_API_KEY = os.getenv("APIFY_API")
  print(APIFY_API_KEY)
  TEST = os.getenv("TEST")
  print(TEST)
  url = "https://api.apify.com/v2/acts/misceres~indeed-scraper/runs?token=" + APIFY_API_KEY
  print(url)

  payload = json.dumps({
    "country": "FR",
    "followApplyRedirects": True,
    "parseCompanyDetails": True,
    "saveOnlyUniqueItems": True,
    "startUrls": [
      {
        "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+€&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28W2F4E%29%3B&fromage=1&vjk=990ae538c5108862"
      }
    ]
  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)
  return response.text


"""scrape data from Indeed website and return a json file with the results"""
def scrape_job_offers(id_dataset):
  APIFY_API_KEY = os.getenv("APIFY_API")
  url = "https://api.apify.com/v2/datasets/" + id_dataset + "/items?format=json&clean=1&token=" + APIFY_API_KEY
  response = requests.get(url)
  return response.json()