"""
test_google_trends_scraper.py

Unit tests for google_trends_scraper.py
"""

import sys
import os
import time
import pandas as pd
from numpy.random import rand
import pytest
from google_trends_scraper.google_trends_scraper import * 

@pytest.fixture
def gts_setup():
    gts = GoogleTrendsScraper("post malone", "2017-01-01", "2017-08-01",
                              email='musicfoxrobot@gmail.com', 
                              psswd='Foci4chI',
                              seconds_delay=0)
    return gts

def test_gts_partition_date():
    start, end = '2017-01-01', '2018-12-20'
    gts = GoogleTrendsScraper("post malone",
                              start,
                              end, 
                              email='musicfoxrobot@gmail.com', 
                              psswd='Foci4chI',
                              seconds_delay=0)
    testlist = gts.partition_dates()
    assert len(testlist) > 0
    assert (testlist[0][0], testlist[-1][1]) == (start, end)
    assert (testlist[-2][1], testlist[-1][0]) == ('2018-11-06', '2018-11-07')
    
