"""
Fetch npm dependency information from the GitHub v4 API
"""

import os.path
import json
import re
import datetime
import requests
import requirements
from .psql import connect_to_db
from .psql import insert_to_app
from .psql import insert_to_dependencies
from .psql import insert_to_package

HEADERS = {"Authorization": "Bearer " + str(os.environ.get('GH_TOKEN'))}
MAX_NODES_PER_LOOP = 100
NUMBER_REGEX = re.compile(r'\d+')

GITHUB_V4_URL = 'https://api.github.com/graphql'


def write_db(database, result, language="JavaScript"):
    """
    Write a set of repositories and their dependencies to the database for JS packages
    """

    nodes = [edge['node'] for edge in result['data']['search']['edges']]
    for node in nodes:
        if not node['object']:
            continue
        package_str = node['object']['text']

        # JavaScript
        if language == "JavaScript":
            package_str = package_str.replace('\n', '').replace('\"', '"')
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

                        # Extract the major version number from the version string
                        result = NUMBER_REGEX.search(value)
                        if not result:
                            continue

                        dependency_str = 'pkg:npm/' + key + "@" + result.group()
                        package_id = insert_to_package(database, dependency_str)
                        insert_to_dependencies(database, str(application_id), str(package_id))
                except AttributeError:
                    continue
        # Python
        elif language == "Python":
            hash_value = hash(package_str)
            application_id = insert_to_app(database,
                                           node['url'],
                                           node['watchers']['totalCount'],
                                           node['nameWithOwner'],
                                           hash_value)
            try:
                for req in requirements.parse(package_str):
                    package_name = req.name
                    if len(req.specs) == 0:
                        package_version = ''
                    else:
                        package_version = req.specs[0][1].split('.')[0]
                    dependency_str = 'pkg:pypi/' + package_name + "@" + package_version
                    package_id = insert_to_package(database, dependency_str)
                    insert_to_dependencies(database, str(application_id), str(package_id))
            # pylint: disable=bare-except
            except:
                print(f"failed fetching for: node['url']")
    database.commit()

def run_query(today, language='JavaScript'):
    """
    Fetch all repositories for the given month
    """

    # set up database
    database = connect_to_db()

    # fetch data and write to database
    last_node = None
    yesterday = today - datetime.timedelta(days=1)
    end_date_str = today.strftime("%Y-%m-%d")
    start_date_str = yesterday.strftime("%Y-%m-%d")
    daily_search_str = "created:" + start_date_str + ".." + end_date_str
    while True:
        try:
            result = run_query_once(MAX_NODES_PER_LOOP, daily_search_str, last_node, language)
            write_db(database, result, language)
            if len(result['data']['search']['edges']) > 0:
                last_node = result['data']['search']['edges'][-1]['cursor']
            else:
                break
        except ValueError as exc:
            # pylint: disable=line-too-long
            print(f"Could not run query starting at {last_node} for {daily_search_str}: {exc}: {result}")
            break
        except TypeError as exc:
            # pylint: disable=line-too-long
            print(f"Could not run query starting at {last_node} for {daily_search_str}: {exc}: {result}")
            break

    # tear down database connection
    database.close()


def run_query_once(node_per_loop, daily_search_str, cursor, language):

    assert os.environ.get('GH_TOKEN'), "GH_TOKEN not set"

    """
    Fetch a single page of repositories for the given month
    """
    if language == "JavaScript":
        expression_string = "master:package.json"
    elif language == "Python":
        expression_string = "master:requirements.txt"
    query = """
        query SearchMostTop10Star($queryString: String!, $maybeAfter: String, $numberOfNodes: Int, $expressionStr: String!) {
        search(query: $queryString, type: REPOSITORY, first: $numberOfNodes, after: $maybeAfter) {
            edges {
            node {
                ... on Repository {
                nameWithOwner
                url
                watchers {
                    totalCount
                }
                object(expression: $expressionStr) {
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

    variables = {
        "queryString": f"language:{language} stars:>1 {daily_search_str}",
        "maybeAfter": cursor,
        "numberOfNodes": node_per_loop,
        "expressionStr": expression_string
    }

    request = requests.post(GITHUB_V4_URL, json={'query': query, 'variables': variables},
                            headers=HEADERS)
    try:
        return request.json()
    except:
        raise Exception("request failed!")
