from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import re
import time
from tqdm import tqdm

# Scrapes just one site for now.
url = 'https://ai-jobs.net'


class Scryer:
    def clicker(self):
        driver = webdriver.Chrome()
        driver.get(url)
        while True:
            time.sleep(1)
            try:
                button = driver.find_element(By.XPATH,
                                             '//*[@id="load-more-jobs"]')
                button.click()

# button.click() will throw an exception every time, this is a bug
# in selenium's code. Simply continue when click fails.
# NoSuchElementException will throw when all data is loaded in the page.

            except ElementClickInterceptedException:
                continue

            except NoSuchElementException:
                print('Done')
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                jobs = soup.find_all('a', href=re.compile(r'/job/\d+'))
                job_links = []
                for link in jobs:
                    job_links.append(link['href'])
                return job_links

    def extracter(self, path_list):
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
                    date = (soup.find('time'))['datetime'][:10]
                    salary = soup.find(
                        'span',
                        class_='badge rounded-pill text-bg-success my-1'
                        ).text
                    exp_level = soup.find(
                        'span', class_='badge rounded-pill text-bg-info my-1'
                        ).text
                    region = soup.find(
                        'div', class_='col').get_text(strip=True)[7:]
                    block.append(
                        {
                            'created_date': date,
                            'description': desc,
                            'salary': salary,
                            'exp_level': exp_level,
                            'region': region
                        }
                                )
                except AttributeError:
                    continue
        return block
