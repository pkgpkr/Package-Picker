import MonthCalculation
import datetime
import GraphQLQuery
import Log
import os


def main():
    Log.clearLog()
    today = datetime.datetime.now()
    for i in range(0, os.environ['MONTH']):
        GraphQLQuery.runQuery(MonthCalculation.monthDelta(today, i))


main()
