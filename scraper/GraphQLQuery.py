import requests
import os.path
import MonthCalculation
import Log
import PSQL
import json

headers = {"Authorization": "Bearer " + os.environ['TOKEN']}
MAX_NODES_PER_LOOP = 100
totalRepos = 0
logPrefix = "./log/"

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

searchQuery = "topic:JavaScript stars:>70 followers:>70 "


# insert name, url, retrieved time
def writeDB(db, result):
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
                pass
            if 'dependencies' in packageJSON:
                # insert applications table only if dependencies exist in package.json
                hashValue = hash(packageStr)
                application_id = PSQL.insertToApplication(db, url, followers, name, hashValue)
                dependencies = packageJSON['dependencies']
                try:
                    for k, v in dependencies.items():
                        if type(v) is not str:
                            pass
                        else:
                            dependencyStr = 'pkg:npm/' + k + "@" + v.replace('^', '').replace('~', '')
                        package_id = PSQL.insertToPackages(db, dependencyStr)
                        PSQL.insertToDependencies(db, str(application_id), str(package_id))
                except:
                    pass
    db.commit()


def runQuery(today):
    # set up database
    db = PSQL.connectToDB()
    monthlySearchStr = MonthCalculation.getMonthlySearchStr(today)
    result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr)
    totalRepos = result['data']['search']['repositoryCount']
    i = 0
    while i * 100 < totalRepos - MAX_NODES_PER_LOOP:
        result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr)
        writeDB(db, result)
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
    writeDB(db, result)
    Log.writeLog(result, today)
    # today = MonthCalculation.monthDelta(today,1)


def runQueryOnce(nodePerLoop, monthlySearchStr):
    f = None
    fileName = logPrefix + "lastNode_" + monthlySearchStr + ".txt"
    if os.path.exists(fileName):
        f = open(fileName, "r")
    variables = {
        "queryString": searchQuery + monthlySearchStr,
        "maybeAfter": f.read() if f else None,
        "numberOfNodes": nodePerLoop
    }
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables},
                            headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code")
