import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from numpy.random import rand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print(f"before path: {sys.path}")

# Adding geckodriver to our path so whoever imports our library can run correctly
sys.path.insert(0, "google_trends_scraper")

print(f"after path: {sys.path}")


class GoogleTrendsScraper:
    original_output_file_name = (
        "multiTimeline.csv"
    )  # the name of the output CSV file from Google Trends

    """Grabs weekly data from start to end for given query
    """

    def __init__(
        self,
        query,
        start_date,
        end_date,
        email,
        psswd,
        output_file_name="output.csv",
        seconds_delay=15,
        weekly_granularity=False,
    ):
        """

        :param query: the query we're scraping
        :param start_date: the start date of the range we're scraping for in format (YYYY-MM-DDD)
        :param end_date: the start date of the range we're scraping for in format (YYYY-MM-DDD)
        :param output_file_name: the name of the output csv
        :param seconds_delay: how long to wait between delays (caution don't set this too low out of fear of being banned)
        :param weekly_granularity: whether Google Trends data should be broken up to many weeks
        """

        self.query = query.replace(" ", "%20")
        self.original_query = query.replace(" ", "_")
        self.start_date = start_date
        self.end_date = end_date
        self.email = email  
        self.psswd = psswd
        self.output_file_name = output_file_name
        self.seconds_delay = seconds_delay
        self.auth_url = 'https://accounts.google.com/signin'
        self.download_path = os.getcwd()
        self.driver = webdriver.Chrome(executable_path = 'google_trends_scraper/chromedriver',
                                       chrome_options = self.get_options())
 

    def auth_google(self):
        self.driver.get(self.auth_url)
        self.driver.implicitly_wait(3)
        self.driver.find_element_by_id("identifierId").send_keys(self.email)
        self.driver.find_element_by_id("identifierNext").click()
        time.sleep(1 + rand() * .5)
        self.driver.find_element_by_css_selector(
            "input[type='password']").send_keys(self.psswd)
        element = self.driver.find_element_by_id('passwordNext')
        self.driver.execute_script("arguments[0].click();", element)
    
    def get_options(self):
        # Add arguments telling Selenium to not actually open a window
        chrome_options = Options()
        download_prefs = {'download.default_directory' : self.download_path,
                          'download.prompt_for_download' : False,
                          'profile.default_content_settings.popups' : 0}
         
        chrome_options.add_experimental_option('prefs', download_prefs)
#        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        return chrome_options 
 
    def generate_url(self, start_date, end_date):
        """Generates a Google Trends URL for a given range

        :param str start_date: the start date
        :param str end_date: the end date

        :return: the formatted Google Trends URL from start to end
        :rtype: str
        """
        base = "https://trends.google.com/trends/explore"
        date = f"date={start_date}%20{end_date}"
        query = "q=" + self.query
        url = f"{base}?{date}&{query}"

        return url

    def fetch_week_trends(self,
                          url,
                          output_file_name=original_output_file_name):
        """Fetch the trends for a given week, in daily granularity

        :param str url: URL to fetch the CSV from
        :param str output_file_name: file path for where to save the CSV file

        :return: None
        """
        # Download the CSV file
        self.driver.get(url)
        self.driver.implicitly_wait(
            2 + rand()
        )  # may need to implicitly wait longer on slow connections
        button = self.driver.find_element_by_class_name("export")
        button.click()
        # wait for the file to download
        start = time.time() 
        while not os.path.exists(self.original_output_file_name):
            t = rand()
            print(f"waiting {t:.2f} second(s), perpetually, " + \
                  f"for file to be downloaded")
            time.sleep(t)
            if start > self.seconds_delay:
                error = f"Could not acquire {self.original_query}" +\
                        f" @ {url} @ {time.time()}"
                raise Exception(error)

        print(f"about to rename {self.original_output_file_name} to " + \
              f"{output_file_name}")
        os.rename(self.original_output_file_name, output_file_name)

    def total_scrape(self, ):
        date_ranges = self.partition_dates()
        files = []
        for start_date, end_date in date_ranges:
            url = self.generate_url(start_date, end_date)
            time.sleep(1 + rand())
            self.fetch_week_trends(url, f"{start_date}_to_{end_date}.csv")
            files.append(
                pd.read_csv(f"{start_date}_to_{end_date}.csv")
            )
            os.remove(f"{start_date}_to_{end_date}.csv")
        self.driver.quit()
        full_df = pd.concat(files) 
        filename = f"{self.original_query}_{self.start_date}" + \
                   f"_to_{self.end_date}.csv"
        full_df.to_csv(filename,
                       index=False)  

        return full_df

    def scrape(self):
        """
        Begin the scrape, returning a DataFrame of the scraped data
        and writing the output to a CSV

        :return: the scraped data
        :rtype: DataFrame
        """
        
        print(os.getcwd())
        self.auth_google()
        return self.total_scrape()

    def combine_csv_files(self, file_names, output=None):
        """
        Combines all given csv file names, of the same structure, to a single one

        :param list file_names: a list of all file names to combine
        :param str output: the filename of the output we'll be making

        :return: None
        """

        # function definition
        if output is None:
            output = self.output_file_name

        dfs = []
        for filename in sorted(file_names):
            dfs.append(pd.read_csv(filename, skiprows=2))
        full_df = pd.concat(dfs)

        full_df.to_csv(output, index=False)  # removes the useless index column

    def partition_dates(self, partition_size = None):
        """Returns a list of dates within an 6-month period, up to the 
           last given date

        As there are about 245 days in any 3-month period, split on this, 
        specifically.
        
        :return: list
        """
        fmt = '%Y-%m-%d'
        # return the difference in days
        if not partition_size:
            partition_size = 75 
        dr = pd.date_range(self.start_date, self.end_date, freq='D')
        date_partitions = []
        efrac = int(np.floor(len(dr) / partition_size))
        for partition in np.arange(0,
                                   efrac * partition_size,
                                   partition_size):
            bottom, top = partition, partition + partition_size
            start = str(dr[bottom:top][0].date())
            end = str(dr[bottom:top][-1].date())
            date_partitions.append((start, end))

        remainder = len(dr) - (partition_size * efrac)     
        start = str(dr[partition_size * efrac: len(dr)][0].date())
        date_partitions.append((start, self.end_date))

        return date_partitions
