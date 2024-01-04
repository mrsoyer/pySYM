import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time


"scrape job offers from meteojob.com"
def scrape_job_offers(url):
    result = {"results": []}

    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    # print(soup.prettify())
    jobs_list = soup.find("ul", class_="list-group ng-star-inserted")
    # print(jobs_list)
    job = jobs_list.find("li", class_="list-group-item cc-list-group-item cc-border-none cc-radius-0 p-4 cc-cursor-pointer cc-bg-gray-bright-hover ng-star-inserted")
    job_id = job.get("id")
    job_title = job.find("h2", class_="cc-cursor-pointer text-truncate cc-job-offer-title cc-job-offer-title-hover cc-font-size-large mb-0 mt-1").text
    company_name = job.find("p", class_="d-inline-block mt-1 mb-0 ng-star-inserted").text
    company_location = job.find("div", class_="mr-3 mb-1 cc-font-size-small mb-lg-3 mr-lg-0").text
    contract_type = job.find("div", class_="mb-1 cc-font-size-small d-flex flex-row ng-star-inserted").text
    salary = job.find("div", class_="d-flex mr-2 mt-1 ng-star-inserted").text

    # print(f"""
    # job_id: {job_id},
    # job_title: {job_title},
    # company_name: {company_name},
    # company_location: {company_location},
    # contract_type: {contract_type},
    # salary: {salary}
    # """)

    for job in jobs_list.find_all("li", class_="list-group-item cc-list-group-item cc-border-none cc-radius-0 p-4 cc-cursor-pointer cc-bg-gray-bright-hover ng-star-inserted"):
        # job = jobs_list.find("li", class_="list-group-item cc-list-group-item cc-border-none cc-radius-0 p-4 cc-cursor-pointer cc-bg-gray-bright-hover ng-star-inserted")
        # print(job)
        # break
        res = {}
        res["job_id"] = job.get("id")
        res["job_title"] = job.find("h2", class_="cc-cursor-pointer text-truncate cc-job-offer-title cc-job-offer-title-hover cc-font-size-large mb-0 mt-1").text
        res["company_name"] = job.find("p", class_="d-inline-block mt-1 mb-0 ng-star-inserted").text
        res["company_location"] = job.find("div", class_="mr-3 mb-1 cc-font-size-small mb-lg-3 mr-lg-0").text
        res["contract_type"] = job.find("div", class_="mb-1 cc-font-size-small d-flex flex-row ng-star-inserted").text
        if job.find("div", class_="d-flex mr-2 mt-1 ng-star-inserted"):
            res["salary"] = job.find("div", class_="d-flex mr-2 mt-1 ng-star-inserted").text
        else:
            res["salary"] = "not available"

        result["results"].append(res)
        # print(job)
        # break
        print(res["job_title"])
    print(len(result["results"]))

    # """get the next page url"""
    # next_page = soup.find("a", class_="cc-pagination-next cc-cursor-pointer cc-pagination-link cc-pagination-link-hover cc-pagination-link-active")
    # next_page_url = next_page.get("href")
    # print(next_page_url)

    "execute js script to get the next page"
    driver = webdriver.Chrome(executable_path="/home/amine/Downloads/chromedriver_linux64/chromedriver")
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    for job in jobs_list.find_all("li", class_="list-group-item cc-list-group-item cc-border-none cc-radius-0 p-4 cc-cursor-pointer cc-bg-gray-bright-hover ng-star-inserted"):
        # job = jobs_list.find("li", class_="list-group-item cc-list-group-item cc-border-none cc-radius-0 p-4 cc-cursor-pointer cc-bg-gray-bright-hover ng-star-inserted")
        # print(job)
        # break
        res = {}
        res["job_id"] = job.get("id")
        res["job_title"] = job.find("h2", class_="cc-cursor-pointer text-truncate cc-job-offer-title cc-job-offer-title-hover cc-font-size-large mb-0 mt-1").text
        res["company_name"] = job.find("p", class_="d-inline-block mt-1 mb-0 ng-star-inserted").text
        res["company_location"] = job.find("div", class_="mr-3 mb-1 cc-font-size-small mb-lg-3 mr-lg-0").text
        res["contract_type"] = job.find("div", class_="mb-1 cc-font-size-small d-flex flex-row ng-star-inserted").text
        if job.find("div", class_="d-flex mr-2 mt-1 ng-star-inserted"):
            res["salary"] = job.find("div", class_="d-flex mr-2 mt-1 ng-star-inserted").text
        else:
            res["salary"] = "not available"

        result["results"].append(res)
        # print(job)
        # break
        print(res["job_title"])
    print(len(result["results"]))

    return result

url = "https://www.meteojob.com/jobs?where=Bouches-du-Rh%C3%B4ne%20(13)"
scrape_job_offers(url)