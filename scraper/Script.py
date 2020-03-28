import MonthCalculation
import datetime
import GitHubQuery
import NpmQuery
import Log
import os


def main():
    Log.clearLog()
    today = datetime.datetime.now()

    # Fetch applications from GitHub
    for i in range(0, int(os.environ['MONTH'])):
        print("Fetching month " + str(i) + " of " + os.environ['MONTH'])
        GitHubQuery.runQuery(MonthCalculation.monthDelta(today, i))
    
    # Fetch package metadata from npmjs.com
    NpmQuery.runQuery()

main()
