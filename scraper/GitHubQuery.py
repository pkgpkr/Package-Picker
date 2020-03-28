import requests
import os.path
import MonthCalculation
import Log
import PSQL
import json
import re

headers = {"Authorization": "Bearer " + os.environ['TOKEN']}
MAX_NODES_PER_LOOP = 100
totalRepos = 0
logPrefix = "./log/"
numberRegex = re.compile(r'\d+')

query = """
    query SearchMostTop10Star($queryString: String!, $maybeAfter: String, $numberOfNodes: Int) {
    search(query: $queryString, type: REPOSITORY, first: $numberOfNodes, after: $maybeAfter) {
        edges {
        node {
            ... on Repository {
            nameWithOwner
            url
            watchers {
                totalCount
            }
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

searchQuery = "topic:JavaScript stars:>1"


# insert name, url, retrieved time
def writeDB(db, cur, result):
    nodes = result['data']['search']['edges']
    for n in nodes:
        url = n['node']['url']
        name = n['node']['nameWithOwner']
        followers = n['node']['watchers']['totalCount']

        if not (n['node']['object'] is None):
            packageStr = n['node']['object']['text'].replace('\n', '').replace('\"', '"')
            # TODO: sometimes package.json is corrupted, skip them first
            try:
                packageJSON = json.loads(packageStr)
            except:
                continue
            if 'dependencies' in packageJSON:
                # insert applications table only if dependencies exist in package.json
                hashValue = hash(packageStr)
                application_id = PSQL.insertToApplication(cur, url, followers, name, hashValue)
                dependencies = packageJSON['dependencies']
                try:
                    for k, v in dependencies.items():
                        if type(v) is not str:
                            continue
                        else:
                            # Extract the major version number from the version string
                            result = numberRegex.search(v)
                            if (result):
                                dependencyStr = 'pkg:npm/' + k + "@" + result.group()
                            else:
                                continue
                        package_id = PSQL.insertToPackages(cur, dependencyStr, None, None, None)
                        PSQL.insertToDependencies(cur, str(application_id), str(package_id))
                except:
                    continue
    db.commit()


def runQuery(today):
    # set up database
    db = PSQL.connectToDB()
    cur = db.cursor()

    # fetch data and write to database
    monthlySearchStr = MonthCalculation.getMonthlySearchStr(today)
    result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr)
    totalRepos = result['data']['search']['repositoryCount']
    i = 0
    while i * 100 < totalRepos - MAX_NODES_PER_LOOP:
        result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr)
        writeDB(db, cur, result)
        i += 1
        lastNode = result['data']['search']['edges'][-1]['cursor']
        fileName = logPrefix + "lastNode_" + monthlySearchStr + ".txt"
        if not os.path.exists(logPrefix):
            os.mkdir(logPrefix)
        f = open(fileName, "w")
        f.write(lastNode)
        f.close()
        Log.writeLog(result, today)
    result = runQueryOnce(totalRepos - i * 100, monthlySearchStr)
    writeDB(db, cur, result)
    Log.writeLog(result, today)
    
    # tear down database connection
    cur.close()
    db.close()


def runQueryOnce(nodePerLoop, monthlySearchStr):
    f = None
    fileName = logPrefix + "lastNode_" + monthlySearchStr + ".txt"
    if os.path.exists(fileName):
        f = open(fileName, "r")
    variables = {
        "queryString": f"{searchQuery} {monthlySearchStr}",
        "maybeAfter": f.read() if f else None,
        "numberOfNodes": nodePerLoop
    }
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables},
                            headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code")
