import MonthCalculation
import datetime
import GraphQLQuery
import Log
import PSQL

def main():
    Log.clearLog()
    today = datetime.datetime.now()
    for i in range(0, 120):
        GraphQLQuery.runQuery(MonthCalculation.monthdelta(today, i)) 

main()