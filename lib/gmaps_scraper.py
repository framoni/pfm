import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GmapsScraper:

    def __init__(self, user_agent='Chrome/103.0.5060.114', headless=True, implicit_wait=5):
        self.user_agent = user_agent
        self.headless = headless
        self.implicit_wait = implicit_wait

        self.options = webdriver.ChromeOptions()
        if self.headless:
            self.options.add_argument('headless')
        self.options.add_argument(f'user-agent={user_agent}')

    def start(self):
        """Start the browser and head to the Google Maps page."""
        self.browser = webdriver.Chrome(options=self.options)
        self.browser.implicitly_wait(self.implicit_wait)
        self.browser.get('https://www.google.it/maps')
        try:
            button = self.browser.find_element(By.XPATH, '//input[@aria-label="Reject all"]')
            button.click()
        except NoSuchElementException:
            logging.warning('Google TOS "Reject All" button was not found')

    def stop(self):
        """Stop the browser."""
        self.browser.close()

    def search(self, query):
        """Find search bar, input the query string, run search."""
        search_input = self.browser.find_element(by=By.ID, value='searchboxinput')
        search_input.send_keys(query)
        search_button = self.browser.find_element(by=By.ID, value='searchbox-searchbutton')
        search_button.click()

    def scrape_hits(self):
        """Scrape search results for business types."""
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, '//img[@alt="Directions"]')))
        text = self.browser.find_element(By.XPATH, "/html/body").text
        with open('../gmaps_types_en.txt', 'r') as f:
            types = f.read().splitlines()
        type_counts = {}
        for t in types:
            type_counts[t] = len([m.start() for m in re.finditer(t, text)])
        return type_counts

    def get_gmaps_type(self, name):
        """Get the most likely business type for a given name."""
        self.search(name)
        type_counts = self.scrape_hits()
        type_counts_sorted = {k: v for k, v in sorted(type_counts.items(), key=lambda item: item[1], reverse=True)}
        return list(type_counts_sorted.keys())[0]