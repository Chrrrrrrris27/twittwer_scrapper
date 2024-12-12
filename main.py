from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

from DB_connection.sql_connection import sqlConnection

class main():

    paths = {
        "user": {
            "name": '//input[@autocomplete="username"]',
            "pass": '//input[@name="password"]'
        },
        "buttons": {
            "search": '//input[@placeholder="Search Twitter"]'
        },
        "elements": {
            "tweet": '//div[@data-testid="tweetText"]',
            "date": '//div[@data-testid="User-Name"]/time'
        },
        "json_file": 'tweets.json'
    }

    dates = [
        {
            "since": "2023-01-01",
            "until": "2023-01-31"
        },
        {
            "since": "2023-02-01",
            "until": "2023-02-28"
        },
        {
            "since": "2023-03-01",
            "until": "2023-03-31"
        }
    ]
    companies = []
    tweets_json = {}

    def __init__(self):
        load_dotenv()
        
        self.sql_connection = sqlConnection()
        self.companies = self.sql_connection.get_companies()

        for company in self.companies:
            self.tweets_json[company["name"]] = []
            

        self.driver = webdriver.Firefox()
        self.driver.get(os.environ.get('ROOT'))
        
        self.auth_user()

        self.get_data()

        
    def auth_user(self):
        user_name = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, self.paths["user"]["name"]))
        )
        user_name.clear()
        user_name.send_keys(os.environ.get('USER_NAME'))
        time.sleep(3)
        user_name.send_keys(Keys.RETURN)

        user_pass = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, self.paths["user"]["pass"]))
            )
        user_pass.clear()
        # user_pass.send_keys(os.environ.get('USER_PASSWORD'))
        user_pass.send_keys('Prueba#123')
        user_pass.send_keys(Keys.RETURN)
    
    def search_tweets(self, **kwargs):
        if kwargs:
            company = kwargs["company"]
            until = kwargs["until"]
            since = kwargs["since"]
        searcher = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, self.paths["buttons"]["search"]))
        )

        query_serach = f"(to:{company}) until:{until} since:{since}"

        searcher.clear()
        searcher.send_keys(query_serach)
        searcher.send_keys(Keys.RETURN)

    def get_tweets(self, current_height, default_height, company):
        time.sleep(3)

        tweets = self.driver.find_elements(By.XPATH, self.paths["elements"]["tweet"])
        dates = self.driver.find_elements(By.XPATH, self.paths["elements"]["date"])

        tweets = list(set(tweets))
        dates = list(set(dates))

        if len(tweets) <= len(dates):
            for tweet in tweets:
                self.tweets_json[company].append({
                    "tweet": tweet.text,
                    "date": dates[tweets.index(tweet)].get_attribute("datetime")
                })
        else:
            len_diff = len(tweets) - len(dates)
            null_dates = []
            for i in range(len_diff):
                null_dates.append(None)
            dates.extend(null_dates)
            for tweet in tweets:
                if dates[tweets.index(tweet)] is None:
                    self.tweets_json[company].append({
                        "tweet": tweet.text,
                        "date": dates[tweets.index(tweet)]
                    })
                else:
                    self.tweets_json[company].append({
                        "tweet": tweet.text,
                        "date": dates[tweets.index(tweet)].get_attribute("datetime")
                    })

        if current_height > default_height:
            current_height = current_height - default_height
            self.driver.execute_script(f"window.scrollTo(0, {current_height});")
            self.get_tweets(current_height, default_height, company)
        else:
            return
        
    def get_scroll (self, current_height, default_height, company):
        scroll_height = self.driver.execute_script("return document.body.scrollHeight;")
        self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
        if (scroll_height > current_height):
            time.sleep(3)
            self.get_scroll(scroll_height, default_height, company)
        else:
            self.get_tweets(current_height, default_height, company)

    def get_data (self):
        for company in self.companies:
            for date in self.dates:
                self.search_tweets(
                    company = company["user"],
                    until = date["until"],
                    since = date["since"]
                )
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, self.paths["elements"]["tweet"]))
                )
                default_height = self.driver.execute_script("return document.body.scrollHeight;")
                self.get_scroll(0, default_height / 3.5, company["name"])

        self.write_json()

    def write_json (self):
        with open(self.paths["json_file"], 'w') as json_file:
            json.dump(self.tweets_json, json_file)
main()