import sys
import os
import time
import pandas as pd
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
        self.start_date = start_date
        self.end_date = end_date
        self.email = email  
        self.psswd = psswd
        self.output_file_name = output_file_name
        self.seconds_delay = seconds_delay
        self.weekly_granularity = weekly_granularity
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
        #chrome_options.add_argument('--headless')
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
                          output_file_name=original_output_file_name
    ):
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
        while not os.path.exists(self.original_output_file_name):
            t = rand()
            print("waiting {t} second, perpetually, for file to be downloaded")
            time.sleep(t)

        print(f"about to rename {self.original_output_file_name} to {output_file_name}")
        os.rename(self.original_output_file_name, output_file_name)

    def generate_weeks(self, start_date, end_date):
        """Generates all start of the weeks between the start and end, specifically with the same day as Start

        :param str start_date: The start of the range
        :param str end_date: The end of the range

        :return: list of weeks within range
        :rtype: list
        """

        print(f"\tstart:\t{start_date}")
        print(f"\tend:\t{end_date}")

        # Generate every week from start to finish
        dr = pd.date_range(start=start_date, end=end_date, freq="7D")
        print(f"dr {dr}")
        weeks = dr + pd.Timedelta(weeks=1)
        print(f"weeks {weeks}")
        weeks_str = []

        # Converting to a str representation
        for week in list(weeks):
            print(f"week {week}")
            weeks_str.append(str(week.date()))

        for i in range(0, len(weeks_str), 1):
            try:
                start_week = weeks_str[i]
                end_week = weeks_str[i + 1]
            except IndexError as e:
                print(
                    "Warning: End date wasn't at end of week, missing a most recent few days"
                )
                continue

            print(f"week {i}:")
            print(f"\tstart:\t{start_week}")
            print(f"\tend:\t{end_week}")
            print()

        return weeks_str

    def combine_csv_files(self, file_names, output=None):
        """Combines all given csv file names, of the same structure, to a single one

        :param list file_names: a list of all file names to combine
        :param str output: the filename of the output we'll be making

        :return: None
        """

        # How you're supposed to set a default value to a class variable, weird but you can't reference self in the
        # function definition
        if output is None:
            output = self.output_file_name

        dfs = []
        for filename in sorted(file_names):
            dfs.append(pd.read_csv(filename, skiprows=2))
        full_df = pd.concat(dfs)

        full_df.to_csv(output, index=False)  # removes the useless index column

    def weekly_scrape(self):
        weeks = self.generate_weeks(self.start_date, self.end_date)

        for i in range(0, len(weeks), 1):
            start_day = weeks[i]
            end_day = weeks[i + 1]

            url = self.generate_url(start_day, end_day)
            self.fetch_week_trends(url, f"{start_day}_to_{end_day}.csv")
            delay = rand()
            print(f"Waiting {delay} to avoid IP banning")
            time.sleep(delay)

        self.combine_csv_files(["data/multiTimeline1.csv", "data/multiTimeline2.csv"])

    def total_scrape(self):
        url = self.generate_url(self.start_date, self.end_date)
        self.fetch_week_trends(url, f"{self.start_date}_to_{self.end_date}.csv")
        self.driver.close()

        return pd.read_csv(f"{self.start_date}_to_{self.end_date}.csv")

    def scrape(self):
        """Begin the scrape, returning a DataFrame of the scraped data and writing the output to a CSV

        :return: the scraped data
        :rtype: DataFrame
        """

        print(os.getcwd())
        self.auth_google()
        if self.weekly_granularity:
            return self.weekly_scrape()
        else:
            return self.total_scrape()
