from google_trends_scraper.google_trends_scraper import GoogleTrendsScraper

gts = GoogleTrendsScraper("post malone", "2017-07-01", "2018-08-25",
                          email='musicfoxrobot@gmail.com', 
                          psswd='Foci4chI',
                          seconds_delay=0,)

results = gts.scrape()

print(results)
