"""
Scrape data for the ML pipeline
"""

import datetime
import os
from scraper.github import run_query
import scraper.npm as npm
import scraper.pypi as pypi


def main():
    """
    Two-phase data scraper

    1) Scrape repositories with package.json files from GitHub
    2) Scrape package metadata from npmjs.com
    """

    today = datetime.datetime.now()

    # Fetch applications from GitHub for javascript
    for i in range(0, 30 * int(os.environ['MONTH'])):
        print("Fetching day " + str(i) + " for JS")
        run_query(today - datetime.timedelta(days=i))

    # Fetch package metadata from npmjs.com
    npm.run_query()

    # Fetch applications from GitHub for python
    for i in range(0, 30 * int(os.environ['MONTH'])):
        print("Fetching day " + str(i) + " for python")
        run_query((today - datetime.timedelta(days=i)), "Python")

    # Fetch package metadata from pypi.org
    pypi.run_query()

main()
