import requests
import os.path

headers = {"Authorization": "Bearer 739dd886b42bfbafdcb91948dd0fd7cac2891bfc"}
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
searchQuery = "topic:JavaScript"

def runQueryOnce(nodePerLoop): 
    f = None
    if os.path.exists("lastNode.txt"):
        f = open("lastNode.txt", "r")
    variables = {
        "queryString": searchQuery,
        "maybeAfter": f.read() if f else None,
        "numberOfNodes": nodePerLoop
    }
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        
        return request.json()
    else:
        raise Exception("Query failed to run by returning code")

def writeLog(result, count):
    fileName = "log" + str(count) + ".txt"
    print(fileName)
    f = open(fileName, "w")
    nodes = result['data']['search']['edges']
    for n in nodes:
        if n['node']['object'] != None:
            print(n['cursor'])
            f.write(n['node']['nameWithOwner'] + ':\n')
            f.write(('').join(n['node']['object']['text'])) 
            f.write('\n')
    f.close()

def runQuery(): 
    result = runQueryOnce(MAX_NODES_PER_LOOP) 
    totalRepos = result['data']['search']['repositoryCount']
    i = 0
    while (i * 100 < totalRepos - MAX_NODES_PER_LOOP):
        result = runQueryOnce(MAX_NODES_PER_LOOP) 
        i += 1
        lastNode = result['data']['search']['edges'][MAX_NODES_PER_LOOP - 1]['cursor']
        f = open("lastNode.txt", "w")
        f.write(lastNode)
        f.close()
        writeLog(result, i)
    result = runQueryOnce(totalRepos - i * 100)


runQuery()
