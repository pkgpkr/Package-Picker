"""
Utility functions for the web server
"""

import json
import requests

from pkgpkr.settings import GITHUB_USER_INFO_URL
from pkgpkr.settings import GITHUB_GRAPHQL_URL


def get_user_info(token):
    """
    Get the user info associated with the given GitHub token
    :param token: GitHub API token
    :return:
    """

    header = {'Authorization': 'Bearer ' + token}
    url = GITHUB_USER_INFO_URL
    res = requests.get(url, headers=header)
    return res.json()


def is_user_authenticated(token):
    """
    Determine if the user is authenticated
    :param token: GitHub API token
    :return:
    """

    user_info = get_user_info(token)
    if user_info and user_info.get('login'):
        return True

    return False


def get_user_name(token):
    """
    Retrieves name of the authenticated GitHub user
    :param token: GitHub API token
    :return:
    """

    # Call method to get full info
    user_info = get_user_info(token)
    return user_info.get('login')


def get_repositories(token):
    """
    Get the repositories associated with the given GitHub token
    :param token: GitHub API token
    :return:
    """

    user_name = get_user_name(token)

    query = """
            query GetUserRepositories($userString: String!) {
                user(login: $userString) {
                    repositories(first:100) {
                      nodes {
                        updatedAt
                        nameWithOwner
                        object(expression: "master:package.json") {
                            ... on Blob {
                            text
                            }
                        }
                      }
                    }
                }
            }
            """

    variables = f'{{"userString": "{user_name}"}}'

    payload = {'query': query,
               'variables': variables}

    header = {'Authorization': 'Bearer ' + token}

    res = requests.post(GITHUB_GRAPHQL_URL, headers=header, data=json.dumps(payload))

    return res.json()['data']['user']['repositories']['nodes']


def dependencies_name_to_purl(dependencies):
    """
    Convert dependency names to the universal Package URL (PURL) format
    :param dependencies: Array of name@version like names
    """

    purl_dependencies = []

    for name, version in dependencies.items():
        # Remove ~ and ^ from versions
        clean_version = version.strip('~').strip('^')

        purl_dependencies.append(f'pkg:npm/{name}@{clean_version}')

    return purl_dependencies


def get_dependencies(token, repo_full_name, branch_name):
    """
    Gets repository info for a specific repo (from package.json)
    :param token: GitHub token for auth
    :param repo_full_name: repo name with user name
    :param branch_name: specific branch to fetch dependencies for, or MASTER (default)
    :return: dependencies and all branch names
    """

    # Split qualified repo name into user nae and repo name
    user_name, repo_name = repo_full_name.split('/')

    # Query to get package info
    query = """
                  query GetDependencies($userString: String!, $repositoryString: String!, $expression: String!) {
                  repository(name:$repositoryString, owner:$userString){
                    name
                    refs(first: 100, refPrefix: "refs/heads/") {
                          nodes {
                            name
                          }
                    }
                    object(expression:$expression){
                      ... on Blob {
                        text
                      }
                    }
                  }
                }
                """

    # Creat expression with branch name in it
    expression = f"{branch_name}:package.json"

    # Vars for the query
    variables = f"""{{"userString": "{user_name}",
                      "repositoryString": "{repo_name}",
                      "expression": "{expression}"}}
                 """

    # Construct payload for graphql
    payload = {'query': query,
               'variables': variables}

    header = {'Authorization': 'Bearer ' + token}

    # Call v4 API
    res = requests.post(GITHUB_GRAPHQL_URL, headers=header, data=json.dumps(payload))

    # Fetch the text that contains the package.json inner text
    text_response = res.json()['data']['repository']['object']['text']

    # Fetch branch names
    branch_names = [x['name'] for x in res.json()['data']['repository']['refs']['nodes']]

    return parse_dependencies(text_response), branch_names


def parse_dependencies(text_response):
    """
    Take a stringified package.json file and extract its dependencies
    :param text_reponse: A stringified package.json object
    :return:
    """

    # Parse text into JSON to allow further manipulations
    text_response_json = json.loads(text_response)

    # Return only if dependencies are found
    if text_response_json.get('dependencies'):
        # Fetch the dependencies and convert into P-URLs pkg:npm/scope/name@version
        return dependencies_name_to_purl(text_response_json['dependencies'])

    return []
