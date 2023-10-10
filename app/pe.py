import requests
from bs4 import BeautifulSoup

def test(url):
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


"""scrape data from website and return a json file with the results"""
def scrape_job_offers(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    result = {"results": []}

    for title in soup.find_all("li", class_="result"):
        res = {}
        res["job_title"] = title.find("h2", class_="media-heading").text
        res["job_reference"] = title.find("h2", class_="media-heading").get("data-intitule-offre")
        """get company name"""
        cname = title.find("p", class_="subtext")
        if len(cname) > 1:
            # name = cname.contents[0].strip()
            # res["company_name"] = name
            result["results"].append(res)

    next_20 = soup.find("a", class_="btn btn-primary")
    if next_20:
        result["next_20"] = next_20.get("href")
    return result


"""get all the job's titles and references from the url"""
def get_all_job_titles_and_references(url):
    result = {"results": []}
    data = scrape_job_offers(url)
    while data["next_20"]:
        for job in data["results"]:
            result["results"].append(job)
        if data["next_20"] != "#":
            next = "https://candidat.pole-emploi.fr" + data["next_20"]
            data = scrape_job_offers(next)
        else:
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
    if company.find("h3"):
        result["company_name"] = company.find("h3").text.replace("\n", "")
    if company.find("p"):
        result["company_size"] = company.find("p").text.replace("\n", "")
    else:
        result["company_size"] = "not available"
    for element in soup.find_all(itemprop="address"):
        result["company_city"] = element.find(itemprop="addressLocality").get('content')
        result["company_postal_code"] = element.find(itemprop="postalCode").get('content')
        result["company_region"] = element.find(itemprop="addressRegion").get('content')
        result["company_country"] = element.find(itemprop="addressCountry").get('content')
    
    result["description"] = soup.find("div", class_="description").text.replace("\n", "")
    result["experience"] = soup.find(itemprop="experienceRequirements").text.replace("\n", "")
    result["skills_list"] = []
    for skill in soup.find_all("ul", class_="skill-list list-unstyled"):
            result["skills_list"].append(skill.text)
    result["skills_list"].pop(0)
    for element in soup.find_all("div", class_="description-aside"):
        result["contract_type"] = element.find("dd").text.replace("\n", "")
        result["hours"] = element.find(itemprop="workHours").text.replace("\n", "")
        result["salary"] = element.find("li").text.replace("\n", "")
    return result