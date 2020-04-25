"""
Scrape data for the ML pipeline
"""

import datetime
import os
from scraper.month_calculation import month_delta
from scraper import github
from scraper import npm


def main():
    """
    Two-phase data scraper

    1) Scrape repositories with package.json files from GitHub
    2) Scrape package metadata from npmjs.com
    """

    today = datetime.datetime.now()

    # Fetch applications from GitHub for javascript
    for i in range(0, int(os.environ['MONTH'])):
        print("Fetching month " + str(i) + " of " + os.environ['MONTH'])
        github.run_query(month_delta(today, i))

    # Fetch package metadata from npmjs.com
    npm.run_query()

    # Fetch applications from GitHub for python
    for i in range(0, int(os.environ['MONTH'])):
        print("Fetching month " + str(i) + " of " + os.environ['MONTH'])
        github.run_query(month_delta(today, i), 'Python')


main()
