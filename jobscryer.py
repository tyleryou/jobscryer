from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import re
import time
from tqdm import tqdm
from datetime import datetime

button_path = '//*[@id="load-more-jobs"]' #ai-jobs.net
listing_regex = '/job/\d+'
url = 'https://ai-jobs.net'

class Scraper:
    
    def scrape(self, url, listing_regex=''):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        jobs = soup.find_all('a', href=re.compile(rf'{listing_regex}'))
        job_links = []
        for link in jobs:
            job_links.append(link['href'])
        return job_links
    
    def clicker(self, url, button_path='', listing_regex=''):
        driver = webdriver.Chrome()
        driver.get(url)
        while True:
            time.sleep(1)
            try:
                button = driver.find_element(By.XPATH,
                                             f'{button_path}')
                button.click()

# button.click() will throw an exception every time, this is a bug
# in selenium's code. Simply continue when click fails.
# NoSuchElementException will throw when all data is loaded in the page.

# The button clicker will click the button until there are no more elements 
# to load.

            except ElementClickInterceptedException:
                continue

            except NoSuchElementException:
                print('All buttons clicked')
                job_links = self.scrape(url, listing_regex)
                return job_links

class AIScryer(Scraper):
    # webscrapes ai-jobs.net
    url = 'https://ai-jobs.net'
    listing_regex = '/job/\d+'

    def extract(self, url, path_list):
        itr = len(path_list)
        with tqdm(total=itr, desc='Processing', unit='iterations') as pbar:
            block = []
            for path in path_list:
                pbar.update(1)
                try:
                    r = requests.get(url+path)
                    soup = BeautifulSoup(r.text, 'lxml')
                    descriptions = (soup.find(
                        'div', class_='job-description-text py-3'
                        )).find_all('li')
                    desc = [li.text.strip() for li in descriptions]
                    date = datetime.today().date().strftime('%Y-%m-%d')
                    salary = soup.find(
                        'span',
                        class_='badge rounded-pill text-bg-success my-1'
                        ).text
                    exp_level = soup.find(
                        'span', class_='badge rounded-pill text-bg-info my-1'
                        ).text
                    region = soup.find(
                        'div', class_='col').get_text(strip=True)[7:]
                    location = soup.find(
                        'h3', class_='lead py-3').get_text()
                    if soup.find(
                            'span',
                            class_='badge rounded-pill text-bg-primary'):
                        remote_first = 'Yes'
                    else:
                        remote_first = 'No'
                    title = soup.find(
                        'h1', class_='display-5 mt-4 text-break').get_text()
                    company = soup.find(
                        'h2', class_='h5').get_text()
                    block.append(
                        {
                            'created_date': date,
                            'description': desc,
                            'salary': salary,
                            'exp_level': exp_level,
                            'region': region,
                            'title': title,
                            'location': location,
                            'remote_first': remote_first,
                            'company': company
                        }
                                )
                except AttributeError:
                    continue
        return block
    
class IndeedScryer(Scraper):
    # webscrapes ai-jobs.net

    def extract(self, url, path_list):
        itr = len(path_list)
        with tqdm(total=itr, desc='Processing', unit='iterations') as pbar:
            block = []
            for path in path_list:
                pbar.update(1)
                try:
                    r = requests.get(url+path)
                    soup = BeautifulSoup(r.text, 'lxml')
                    descriptions = (soup.find(
                        'div', class_='job-description-text py-3'
                        )).find_all('li')
                    desc = [li.text.strip() for li in descriptions]
                    date = datetime.today().date().strftime('%Y-%m-%d')
                    salary = soup.find(
                        'span',
                        class_='badge rounded-pill text-bg-success my-1'
                        ).text
                    exp_level = soup.find(
                        'span', class_='badge rounded-pill text-bg-info my-1'
                        ).text
                    region = soup.find(
                        'div', class_='col').get_text(strip=True)[7:]
                    location = soup.find(
                        'h3', class_='lead py-3').get_text()
                    if soup.find(
                            'span',
                            class_='badge rounded-pill text-bg-primary'):
                        remote_first = 'Yes'
                    else:
                        remote_first = 'No'
                    title = soup.find(
                        'h1', class_='display-5 mt-4 text-break').get_text()
                    company = soup.find(
                        'h2', class_='h5').get_text()
                    block.append(
                        {
                            'created_date': date,
                            'description': desc,
                            'salary': salary,
                            'exp_level': exp_level,
                            'region': region,
                            'title': title,
                            'location': location,
                            'remote_first': remote_first,
                            'company': company
                        }
                                )
                except AttributeError:
                    continue
        return block
