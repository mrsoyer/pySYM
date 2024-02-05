import requests
import json
import os


def run_apify():
  APIFY_API_KEY = os.getenv("APIFY_API")
  print(APIFY_API_KEY)
  url = "https://api.apify.com/v2/acts/misceres~indeed-scraper/runs?token=" + APIFY_API_KEY

  payload = json.dumps({
    "country": "FR",
    "followApplyRedirects": True,
    "parseCompanyDetails": True,
    "saveOnlyUniqueItems": True,
    "startUrls": [
      # {
      #   "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+€&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28W2F4E%29%3B&fromage=1&vjk=990ae538c5108862"
      # },
      # {
      #     "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+€&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28X42V4%29%3B&fromage=1&vjk=d98f9b58e26e839d"
      # },
      # {
      #     "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+€&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28CPGHF%29%3B&fromage=1&vjk=b798da917d0e2454"
      # },
      # {
      #     "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28ZYCW4%29%3B&fromage=1&vjk=4e56e63d54212219"
      # },
      # {
      #     "url": "https://fr.indeed.com/jobs?q=restauration&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&fromage=1&vjk=c2cb6c06f3265818"
      # },
      # {
      #     "url": "https://fr.indeed.com/jobs?q=vendeur&l=marseille+%2813%29&vjk=9a300edf2d550182"
      # },
      # {
      #     "url": "https://fr.indeed.com/jobs?q=manutentionnaire&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&fromage=1&vjk=b6379d8321e49e7e"
      # },
      # {
      #     "url": "https://fr.indeed.com/emplois?q=garde+d%27enfants&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&fromage=1&vjk=c301cc77210c2fa8"
      # },
      # {
      #     "url": "https://fr.indeed.com/jobs?q=nettoyage&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&fromage=1&vjk=044769625d814d7a"
      # },
      # {
      #     "url": "https://fr.indeed.com/jobs?q=femme+de+chambre&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&fromage=1&vjk=e2ef308691ddaa91"
      # },
      {
        "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28W2F4E%29%3B&radius=50&fromage=1&vjk=e6082095bc6d6b54"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28X42V4%29%3B&radius=50&fromage=1&vjk=0d532bb80e3b7aac"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28CPGHF%29%3B&radius=50&fromage=1&vjk=b7807f1784244566"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%2Ckf%3Acmpsec%28ZYCW4%29%3B&radius=50&fromage=1&vjk=123a7ca78cbbc741"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=1%C2%A0000+%E2%82%AC&l=marseille+(13)&sc=0bf%3Aexrec(),kf%3Acmpsec(ZYCW4)%3B&radius=50&fromage=1"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=restauration&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&radius=50&fromage=1&vjk=0c27635d048fbbea"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=vendeur&l=marseille+%2813%29&radius=50&vjk=fac5442e486818cd"
      },
      {
        "url": "https://fr.indeed.com/jobs?q=manutentionnaire&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&fromage=1&vjk=b6379d8321e49e7e"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=garde+d%27enfants&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&radius=50&fromage=1&vjk=6de9b374cea58490"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=nettoyage&l=marseille+(13)&sc=0bf%3Aexrec()%3B&radius=50&fromage=1"
      },
      {
        "url": "https://fr.indeed.com/emplois?q=femme+de+chambre&l=marseille+%2813%29&sc=0bf%3Aexrec%28%29%3B&radius=50&fromage=1&vjk=49d5f62d992d7aef"
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