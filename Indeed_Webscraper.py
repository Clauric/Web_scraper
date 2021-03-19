import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import timedelta
from datetime import date

scraped_job_titles = []
scraped_job_locations = []
scraped_company_names = []
scraped_salaries = []
scraped_ratings = []
scraped_apply_urls = []
scraped_days = []
scraped_description = []

# PMs
# https://ie.indeed.com/jobs?q=Project+Manager&l=Dublin
# https://ie.indeed.com/jobs?q=Project+Manager&l=Dublin&sort=date&sr=directhire&fromage=7

# BAs
# https://ie.indeed.com/jobs?q=business+analyst&l=Dublin
# https://ie.indeed.com/jobs?q=business+analyst&l=Dublin&sort=date&sr=directhire&fromage=7

# Testers
# https://ie.indeed.com/jobs?q=testers&l=Dublin&sort=date
# https://ie.indeed.com/jobs?q=testers&l=Dublin&sort=date&sr=directhire&fromage=7

# PMOs
# https://ie.indeed.com/jobs?q=pmo&l=Dublin&sort=date
# https://ie.indeed.com/jobs?q=pmo&l=Dublin&sr=directhire&fromage=7&sort=date


start_url = "https://ie.indeed.com/jobs?q=data+analyst&l=Dublin&fromage=7"

link = requests.get(start_url)
site = BeautifulSoup(link.text, "html.parser")

return_res = str(site.find_all('div', attrs={'id': 'searchCountPages'}))

str1 = ""
res = str1.join(return_res)

results = int(int(res.split()[5])/15)

url = "https://ie.indeed.com/jobs?q=data+analyst&l=Dublin&rbl=Dublin&%2480%2C000&sort=date&fromage=7&start="

for i in range(results):
    if i == 0:
        j = "0"
    else:
        j = str(i) + "0"
    
    url1 = url + str(j)

    link = requests.get(url1)

    site = BeautifulSoup(link.text, "html.parser")

    jobs_a = site.find_all(name='a', attrs={'data-tn-element': 'jobTitle'})

    for job in jobs_a:
        job_attrs = job.attrs
        scraped_job_titles.append(job_attrs['title'])

    loc_div = site.find_all('div', attrs={'class': 'recJobLoc'}) 
    
    for loc in loc_div:
        loc_attrs = loc.attrs
        scraped_job_locations.append(loc_attrs['data-rc-loc'])

    company_span = site.find_all('span', attrs={'class': 'company'})

    for span in company_span:
        scraped_company_names.append(span.text.strip())

    jobs_divs = site.find_all('div', attrs={'class': 'jobsearch-SerpJobCard'})

    for div in jobs_divs:
        salary_span = div.find('span', attrs={'class': 'salaryText'})
        if salary_span:
            scraped_salaries.append(salary_span.string.strip())
        else:
            scraped_salaries.append('Not shown')

    jobs_divs = site.find_all('div', attrs={'class': 'jobsearch-SerpJobCard'})

    for div in jobs_divs:
        rating_span = div.find('span', attrs={'class':  'ratingsContent'})
        if rating_span:
            scraped_ratings.append(float(rating_span.text.strip().replace(',', '.')))
        else:
            scraped_ratings.append(None)

    view_job_url = "https://ie.indeed.com/viewjob?jk="

    jobs_div = site.find_all(name='div', attrs={'class': 'jobsearch-SerpJobCard'})

    for div in jobs_div:
        job_id = div.attrs['data-jk']
        apply_url = view_job_url + job_id
        scraped_apply_urls.append(apply_url)

    days_spans = site.find_all('span', attrs={'class': 'date'})

    for day in days_spans:
        day_string = day.text.strip()
        
        if re.findall('[0-9]+', day_string):
            parsed_day = re.findall('[0-9]+', day_string)[0]

            if 'hour' in day_string:
                job_posted_since = (date.today() - timedelta(int(parsed_day) / 24)).strftime("%d/%m/%Y")
            elif 'day' in day_string:
                job_posted_since = (date.today() - timedelta(int(parsed_day))).strftime("%d/%m/%Y")
            elif 'week' in day_string:
                job_posted_since = (date.today() - timedelta(int(parsed_day) * 7)).strftime("%d/%m/%Y")
            elif 'month' in day_string:
                job_posted_since = (date.today() - timedelta(int(parsed_day) * 30)).strftime("%d/%m/%Y")
            else:
                job_posted_since = str(day_string)
        else:
            job_posted_since = date.today().strftime("%d/%m/%Y")

        scraped_days.append(job_posted_since)

jobs_list = pd.DataFrame()

jobs_list["Title"] = pd.Series(scraped_job_titles)
jobs_list["Location"] = pd.Series(scraped_job_locations)
jobs_list["Company name"] = pd.Series(scraped_company_names)
jobs_list["Salary"] = pd.Series(scraped_salaries)
jobs_list["Date posted"] = pd.Series(scraped_days)
jobs_list["URL"] = pd.Series(scraped_apply_urls)
jobs_list["Company rating"] = pd.Series(scraped_ratings)
jobs_list["Description"] = ""

jobs_list.to_csv("Indeed-python.csv", sep = ",", encoding = "UTF-8")

for i in range(len(jobs_list.index)):

    if jobs_list.loc[i, "Description"] != "":
        continue

    link2 = requests.get(jobs_list.loc[i, "URL"])

    site2 = BeautifulSoup(link2.text, "html.parser")

    description = str(site2.find('div', attrs={"id": "jobDescriptionText"}))

    jobs_list["Description"].iloc[i] = description.split('<div class="jobsearch-jobDescriptionText" id="jobDescriptionText">',1)[1]

jobs_list["Description"] = jobs_list["Description"].replace("\n", " --- ", regex=True) 
jobs_list["Description"] = jobs_list["Description"].replace("<div>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("</div>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("<br/>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("<b>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("</li>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("<li>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("</b>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("</p>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("<p>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("<ul>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("</ul>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("<i>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("</i>", "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace("&amp", "&", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('<h2 class="jobSectionHeader">', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('</h2>', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('<h4 class="jobSectionHeader">', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('</h4>', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('<h3 class="jobSectionHeader">', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('</h3>', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('<h1 class="jobSectionHeader">', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('</h1>', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('<h5 class="jobSectionHeader">', "", regex=True)
jobs_list["Description"] = jobs_list["Description"].replace('</h5>', "", regex=True)

file_name = "Indeed DA " + date.today().strftime("%d%m%Y") + ".csv"
jobs_list.to_csv(file_name, sep = ",", encoding = "UTF-8")

# # https://jlgamez.com/how-i-scrape-jobs-data-from-indeed-com-with-python/
# # https://github.com/jlgamez/indeed-jobs-scraper