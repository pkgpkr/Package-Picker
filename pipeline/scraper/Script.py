import MonthCalculation
import datetime
import GitHubQuery
import NpmQuery
import os


def main():
    today = datetime.datetime.now()
    months = int(os.environ.get('MONTH') or '120')

    # Fetch applications from GitHub in a multi-threaded way
    for i in range(months):
        GitHubQuery.runQuery(MonthCalculation.monthDelta(today, i))
    
    # Fetch package metadata from npmjs.com
    NpmQuery.runQuery()

main()
