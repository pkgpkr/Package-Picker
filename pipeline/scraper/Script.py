import MonthCalculation
import datetime
import GitHubQuery
import npm_query
import os


def main():
    today = datetime.datetime.now()

    # Fetch applications from GitHub
    for i in range(0, int(os.environ['MONTH'])):
        print("Fetching month " + str(i) + " of " + os.environ['MONTH'])
        GitHubQuery.runQuery(MonthCalculation.monthDelta(today, i))
    
    # Fetch package metadata from npmjs.com
    npm_query.run_query()

main()
