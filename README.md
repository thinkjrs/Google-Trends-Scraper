# Google-Trends-Scraper

Get daily data for a search query, as reported on
[Google Trends](https://www.google.com/trends/).

#### Dev-Notes

Google only provides daily data for less than 9-month date ranges, 
therefore the application needs to be able to partition a date range longer
than 9 months into smaller intervals.

**TODO**

- test and implement `partition_dates(start, end)`
	- **specification:** `partition_dates` should take in dates and return
a list of tuples containing 8-month ranges with a single excess range that
concatenate to cover the entire input range
	- **tests:** 
		1. `len(testlist) > 0`
		2. `len(testlist itmes[:-1]) == 8`
		3. `len(testlist items[-1]) == 8`
		4. `(testlist[0][0], testlist[-1][1] == (start, end)`

