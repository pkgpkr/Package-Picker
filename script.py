import requests
import os.path
import datetime

headers = {"Authorization": "Bearer " + os.environ['TOKEN']}
MAX_NODES_PER_LOOP = 100
totalRepos = 0


query = """
    query SearchMostTop10Star($queryString: String!, $maybeAfter: String, $numberOfNodes: Int) {
    search(query: $queryString, type: REPOSITORY, first: $numberOfNodes, after: $maybeAfter) {
        edges {
        node {
            ... on Repository {
            nameWithOwner
            object(expression: "master:package.json") {
                ... on Blob {
                text
                }
            }
            }
        }
        cursor
        }
        repositoryCount
    }
    }
    """
searchQuery = "topic:JavaScript stars:>70 followers:>70 "

def runQueryOnce(nodePerLoop, monthlySearchStr): 
    f = None
    if os.path.exists("lastNode_"+monthlySearchStr+".txt"):
        f = open("lastNode_"+monthlySearchStr+".txt", "r")
    variables = {
        "queryString": searchQuery + monthlySearchStr,
        "maybeAfter": f.read() if f else None,
        "numberOfNodes": nodePerLoop
    }
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        print(variables['queryString'])
        return request.json()
    else:
        raise Exception("Query failed to run by returning code")

def writeLog(result, today):
    fileName = today.strftime("%Y_%m_") + "log" + ".txt"
    print(fileName)
    f = open(fileName, "a+")
    nodes = result['data']['search']['edges']
    count = 1
    for n in nodes:
        if n['node']['object'] != None:
            # print(n['cursor'])
            f.write(str(count) + '\n')
            f.write(n['node']['nameWithOwner'] + ':\n')
            f.write(('').join(n['node']['object']['text'])) 
            f.write('\n')
            count += 1
    f.close()

def runQuery(today): 
    monthlySearchStr = getMonthlySearchStr(today)
    result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr) 
    totalRepos = result['data']['search']['repositoryCount']
    i = 0
    while (i * 100 < totalRepos - MAX_NODES_PER_LOOP):
        result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr) 
        i += 1
        lastNode = result['data']['search']['edges'][MAX_NODES_PER_LOOP - 1]['cursor']
        f = open("lastNode_" + monthlySearchStr + ".txt", "w")
        f.write(lastNode)
        f.close()
        writeLog(result, today)
    result = runQueryOnce(totalRepos - i * 100, monthlySearchStr)
    writeLog(result, today)
    today = monthdelta(today,1)
    
def monthdelta(date, delta):
    m, y = (date.month-delta) % 12, date.year + ((date.month)-delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)
    
def getMonthlySearchStr(startDate):
    endDate = monthdelta(startDate, 1)
    endDateStr = endDate.strftime("%Y-%m-%d")
    startDateStr = startDate.strftime("%Y-%m-%d")
    return "created:" + endDateStr + ".." + startDateStr

def main():
    today = datetime.datetime.now()
    for i in range(0, 120):
        runQuery(monthdelta(today, i)) 
main()
