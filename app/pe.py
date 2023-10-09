import requests
from bs4 import BeautifulSoup
import googlemaps
import os
# from dotenv import load_dotenv


"""scrape data from website and return a json file with the results"""
def scrape_job_offers(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    result = {"results": []}
    for title in soup.find_all("h2", class_="media-heading"):
        res = {}
        res["job_title"] = title.text
        res["job_reference"] = title.get("data-intitule-offre")
        
        result["results"].append(res)
    next_20 = soup.find("a", class_="btn btn-primary")
    if next_20:
        result["next_20"] = next_20.get("href")
    return result

"""scrape job's details from the job's reference"""
def scrape_job_details(ref):
    url = "https://candidat.pole-emploi.fr/offres/recherche/detail/"
    url += ref
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    result["ref"] = ref    
    company = soup.find("div", class_="media-body")
    result["company_name"] = company.find("h3").text.replace("\n", "")
    result["company_size"] = company.find("p").text.replace("\n", "")
    for element in soup.find_all(itemprop="address"):
        result["company_city"] = element.find(itemprop="addressLocality").get('content')
        result["company_postal_code"] = element.find(itemprop="postalCode").get('content')
        result["company_region"] = element.find(itemprop="addressRegion").get('content')
        result["company_country"] = element.find(itemprop="addressCountry").get('content')
    
    result["description"] = soup.find("div", class_="description").text.replace("\n", "")
    result["experience"] = soup.find(itemprop="experienceRequirements").text.replace("\n", "")
    result["skills_list"] = []
    for skills in soup.find_all("ul", class_="skill-list list-unstyled"):
        result["skills_list"].append(skills.text)
    for element in soup.find_all("div", class_="description-aside"):
        result["contract_type"] = element.find("dd").text.replace("\n", "")
        result["hours"] = element.find(itemprop="workHours").text.replace("\n", "")
        result["salary"] = element.find("li").text.replace("\n", "")
    return result

"""get company info from google maps"""
def get_company_info(company_name, city):
    GMAPS_API_KEY = os.getenv("GMAPS_API_KEY")
    gmaps = googlemaps.Client(key=GMAPS_API_KEY)
    place_results = gmaps.places(query=f"{company_name} {city}")

    if place_results['status'] == 'OK' and len(place_results['results']) > 0:
        place = place_results['results'][0]

        place_details = gmaps.place(place_id=place['place_id'], fields=['website', 'formatted_phone_number', 'formatted_address', 'geometry', 'name'])
        if place_details['status'] == 'OK':
            name = place_details['result'].get('name', 'not available')
            address = place_details['result'].get('formatted_address', 'not available')
            website = place_details['result'].get('website', "not available")
            phone = place_details['result'].get('formatted_phone_number', "not available")
            lat = place_details['result']['geometry']['location']['lat']
            lng = place_details['result']['geometry']['location']['lng']

        return {
            "company_name": name,
            'adresss': address,
            'website': website,
            "phone": phone,
            'lat': lat,
            'lng': lng
        }
    else:
        return None