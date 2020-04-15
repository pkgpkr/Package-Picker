"""
Fetch npm dependency information from the GitHub v4 API
"""

import os.path
import json
import re
import requests
from month_calculation import get_monthly_search_str
from psql import connect_to_db
from psql import insert_to_app
from psql import insert_to_dependencies
from psql import insert_to_package

HEADERS = {"Authorization": "Bearer " + os.environ['TOKEN']}
MAX_NODES_PER_LOOP = 100
NUMBER_REGEX = re.compile(r'\d+')

QUERY = """
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

SEARCH_QUERY = "topic:JavaScript stars:>1"
GITHUB_V4_URL = 'https://api.github.com/graphql'


def write_db(database, result):
    """
    Write a set of repositories and their dependencies to the database
    """

    nodes = [edge['node'] for edge in result['data']['search']['edges']]
    for node in nodes:
        if not node['object']:
            continue
        package_str = node['object']['text'].replace('\n', '').replace('\"', '"')
        try:
            # Skip any repositories with a corrupt package.json
            package_json = json.loads(package_str)
        except ValueError:
            continue
        if 'dependencies' in package_json:
            # insert applications table only if dependencies exist in package.json
            hash_value = hash(package_str)
            application_id = insert_to_app(database,
                                           node['url'],
                                           node['watchers']['totalCount'],
                                           node['nameWithOwner'],
                                           hash_value)
            dependencies = package_json['dependencies']
            try:
                for key, value in dependencies.items():
                    if not isinstance(value, str):
                        continue

                    dependency_str = 'pkg:npm/' + key# + "@" + result.group()
                    package_id = insert_to_package(database, dependency_str)
                    insert_to_dependencies(database, str(application_id), str(package_id))
            except AttributeError:
                continue
    database.commit()

def fetch_repos(repos):

    # Query string
    repo_query = """
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
            }
        }
    """

    # Fetch up to 100 repositories
    repo_query_vars = {
        "queryString": ' '.join([f"repo:{repo}" for repo in repos[:100]]),
        "maybeAfter": None,
        "numberOfNodes": MAX_NODES_PER_LOOP
    }

    # Connect to database
    database = connect_to_db()

    # Get Express
    request = requests.post(GITHUB_V4_URL, json={'query': repo_query, 'variables': repo_query_vars},
                            headers=HEADERS)
    result = request.json()

    # Parse the package.json
    nodes = [edge['node'] for edge in result['data']['search']['edges']]
    for node in nodes:
        package_str = node['object']['text'].replace('\n', '').replace('\"', '"')
        package_json = json.loads(package_str)

        # Insert into database
        hash_value = hash(package_str)
        application_id = insert_to_app(database,
                                       node['url'],
                                       node['watchers']['totalCount'],
                                       node['nameWithOwner'],
                                       hash_value)
        dependencies = package_json['dependencies']

        for key, value in dependencies.items():
            if not isinstance(value, str):
                continue

            dependency_str = 'pkg:npm/' + key
            package_id = insert_to_package(database, dependency_str)
            insert_to_dependencies(database, str(application_id), str(package_id))

    # Commit changes and close the database connection
    database.commit()
    database.close()

def run_query(today):
    """
    Fetch all repositories for the given month
    """

    # set up database
    database = connect_to_db()

    # fetch data and write to database
    last_node = None
    monthly_search_str = get_monthly_search_str(today)
    while True:
        try:
            result = run_query_once(MAX_NODES_PER_LOOP, monthly_search_str, last_node)
            write_db(database, result)
            if len(result['data']['search']['edges']) > 0:
                last_node = result['data']['search']['edges'][-1]['cursor']
            else:
                break
        except ValueError:
            print(f"Could not run query starting at {last_node} for {monthly_search_str}")
            break

    # tear down database connection
    database.close()


def run_query_once(node_per_loop, monthly_search_str, cursor):
    """
    Fetch a single page of repositories for the given month
    """

    variables = {
        "queryString": f"{SEARCH_QUERY} {monthly_search_str}",
        "maybeAfter": cursor,
        "numberOfNodes": node_per_loop
    }
    request = requests.post(GITHUB_V4_URL, json={'query': QUERY, 'variables': variables},
                            headers=HEADERS)
    try:
        return request.json()
    except:
        raise Exception("request failed!")
