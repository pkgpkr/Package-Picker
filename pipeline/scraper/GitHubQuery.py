import requests
import os.path
from MonthCalculation import *
from PSQL import *
import json
import re

headers = {"Authorization": "Bearer " + os.environ['TOKEN']}
MAX_NODES_PER_LOOP = 100
totalRepos = 0
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
GITHUB_V4_URL = 'https://api.github.com/graphql'


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
                continue
            if 'dependencies' in packageJSON:
                # insert applications table only if dependencies exist in package.json
                hashValue = hash(packageStr)
                application_id = insertToApplication(db, url, followers, name, hashValue)
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
                        package_id = insertToPackages(db, dependencyStr)
                        insertToDependencies(db, str(application_id), str(package_id))
                except:
                    continue
    db.commit()


def runQuery(today):
    # set up database
    db = connectToDB()

    # fetch data and write to database
    lastNode = None
    monthlySearchStr = getMonthlySearchStr(today)
    while True:
        try:
            result = runQueryOnce(MAX_NODES_PER_LOOP, monthlySearchStr, lastNode)
            writeDB(db, result)
            if len(result['data']['search']['edges']) > 0:
                lastNode = result['data']['search']['edges'][-1]['cursor']
            else:
                break
        except:
            print(f"Could not run query starting at {lastNode} for {monthlySearchStr}")
            break

    # tear down database connection
    db.close()


def runQueryOnce(nodePerLoop, monthlySearchStr, cursor):
    variables = {
        "queryString": f"{searchQuery} {monthlySearchStr}",
        "maybeAfter": cursor,
        "numberOfNodes": nodePerLoop
    }
    request = requests.post(GITHUB_V4_URL, json={'query': query, 'variables': variables},
                            headers=headers)
    try:
        return request.json()
    except:
        raise Exception("request failed!")
