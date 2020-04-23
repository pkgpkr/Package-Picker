"""
Scrape data for the ML pipeline
"""

import datetime
import os
import month_calculation
from github_query import run_query
import npm_query


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
        run_query(month_calculation.month_delta(today, i))

    # Fetch package metadata from npmjs.com
    npm_query.run_query()

    # Fetch applications from GitHub for python
    for i in range(0, int(os.environ['MONTH'])):
        print("Fetching month " + str(i) + " of " + os.environ['MONTH'])
        run_query(month_calculation.month_delta(today, i), 'Python')


main()
