from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
import requests
import re
import time
from tqdm import tqdm
from datetime import datetime


class Scraper:

    def scrape(self, text, listing_regex=''):
        soup = BeautifulSoup(text, 'html.parser')
        jobs = soup.find_all('a', href=re.compile(rf'{listing_regex}'))
        # Some sites have multiple of the same URL listed for individual jobs.
        # This just checks to see if the script has grabbed the URL already.
        job_links = []
        for job in jobs:
            if job['href'] not in job_links:
                job_links.append(job['href'])
        return job_links

    def button_press(self, url, popup_path='', button_path='', sort_path=''):
        driver = webdriver.Chrome()
        driver.get(url)
        button = driver.find_element(By.XPATH,
                                     rf'{button_path}')
        if popup_path:
            try:
                # button = driver.find_element(By.XPATH,
                #                             rf'{button_path}')
                button.click()
            except ElementClickInterceptedException:
                time.sleep(2)
                button_popup = driver.find_element(By.XPATH,
                                                   rf'{popup_path}')
                button_popup.click()
        if sort_path:
            button_sort = driver.find_element(By.XPATH,
                                              rf'{sort_path}')
            button_sort.click()
        # Click the "Load More" button three times, this is overkill as
        # there aren't that many jobs posted every day. The script runs daily,
        # so all fresh jobs are guaranteed. 4 iterations because the first
        # always fails. Absolutely no clue why. Possibly bug in Selenium?
        itr = 0
        while itr < 4:
            time.sleep(1)
            try:
                # button = driver.find_element(By.XPATH,
                #                             rf'{button_path}')
                button.click()
                itr += 1

    # button.click() will throw an exception every time. I have no idea why.
    # Trying to click it again will always work.
    # NoSuchElementException will throw when all data is loaded in the page.
    # Currently commented out, leaving in for data dumps.

            except ElementClickInterceptedException:
                continue

            # except (
                    # NoSuchElementException,
                    # ElementNotInteractableException):
                        # return driver.page_source
            return driver.page_source


class AIScryer(Scraper):
    # webscrapes ai-jobs.net

    url = 'https://ai-jobs.net'
    listing_regex = r'/job/\d+'

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


class RemotiveScryer(Scraper):
    # As much as I don't like repeating code, there's so much nuance in the
    # html to extract from each site that as of right now, I don't know how to
    # make this into one solid method.
    def extract(self, path_list, url=''):
        itr = len(path_list)
        with tqdm(total=itr, desc='Processing', unit='iterations') as pbar:
            block = []
            for path in path_list:
                pbar.update(1)
                try:
                    r = requests.get(url+path)
                    soup = BeautifulSoup(r.text, 'lxml')
                    description = (soup.find(
                        'div', class_='tw-mt-8'
                        )).text
                    date = datetime.today().date().strftime('%Y-%m-%d')
                    salary = soup.find(
                        'span',
                        class_='job-tile-salary tag-small ' +
                        'remotive-tag-light tw-flex'
                        ).text.strip()
                    exp_level = 'NULL'
                    region = soup.find(
                        'span',
                        class_='job-tile-location tag-small ' +
                        'remotive-tag-light tw-flex').text.strip()
                    location = soup.find_all(
                        'span',
                        class_='tw-uppercase ' +
                        'remotive-text-light')[1].text.strip()
                    title = soup.find(
                        'span', class_='h1 remotive-text-bigger').text
                    remote_first = 'NULL'
                    company = soup.find(
                        'span', class_='tw-underline').text
                    block.append(
                        {
                            'created_date': date,
                            'description': description,
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
    
    

