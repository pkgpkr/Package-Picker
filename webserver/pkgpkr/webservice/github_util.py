import requests
import json

from pkgpkr.settings import GITHUB_USER_INFO_URL
from pkgpkr.settings import GITHUB_GRAPHQL_URL


def get_user_info(token):
    header = {'Authorization': 'Bearer ' + token}
    url = GITHUB_USER_INFO_URL
    res = requests.get(url, headers=header)
    return res.json()


def is_user_authenticated(token):
    user_info = get_user_info(token)
    if user_info and user_info.get('login'):
        return True
    else:
        return False


def get_user_name(token):
    """
    Retrieves name of the authenticated GitHub user
    :param token: github api token
    :return:
    """

    # Call method to get full info
    user_info = get_user_info(token)
    return user_info.get('login')


def get_repositories(token):
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


def depenencies_name_to_purl(depencencies):
    purl_dependencies = []

    for name, version in depencencies.items():
        # Remove ~ and ^ from versions
        clean_version = version.strip('~').strip('^')

        purl_dependencies.append(f'pkg:npm/{name}@{clean_version}')

    return purl_dependencies




def get_dependencies(token, repo_full_name):
    """
    Gets repository info for a specific repo (from package.json)
    :param repo_full_name:
    :return:
    """
    # Split qualified repo name into user nae and repo name
    user_name, repo_name = repo_full_name.split('/')

    # Query to get package info
    query = """
                query GetDependencies($userString: String!, $repositoryString: String!) {
                  repository(name:$repositoryString, owner:$userString){
                    name
                    object(expression:"master:package.json"){
                      ... on Blob {
                        text
                      }
                    }
                  }
                }
                """

    # Vars for the query
    variables = f'{{"userString": "{user_name}", "repositoryString": "{repo_name}"}}'

    # Construct payload for graphql
    payload = {'query': query,
               'variables': variables}

    header = {'Authorization': 'Bearer ' + token}

    # Call v4 API
    res = requests.post(GITHUB_GRAPHQL_URL, headers=header, data=json.dumps(payload))

    # Fetch the text that contains the package.json inner text
    text_response = res.json()['data']['repository']['object']['text']


    return parse_dependencies(text_response)


def parse_dependencies(text_response):
    # Parse text into JSON to allow further manipulations
    text_response_json = json.loads(text_response)

    # Return only if dependencies are found
    if text_response_json.get('dependencies'):
        # Fetch the dependencies and convert into P-URLs pkg:npm/scope/name@version
        return depenencies_name_to_purl(text_response_json['dependencies'])