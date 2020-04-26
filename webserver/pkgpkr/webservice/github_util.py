"""
Utility functions for the web server
"""

import json
import requests
import requirements

from pkgpkr.settings import GITHUB_USER_INFO_URL, SUPPORTED_LANGUAGES, JAVASCRIPT, PYTHON
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
            query GetUserRepositories($userString: String!) {{
                user(login: $userString) {{
                    repositories(first:100) {{
                      nodes {{
                        updatedAt
                        nameWithOwner
                        object(expression: "master:{0}") {{
                            ... on Blob {{
                            text
                            }}
                        }}
                      }}
                    }}
                }}
            }}
            """

    variables = f'{{"userString": "{user_name}"}}'

    combined_nodes = dict()

    for language, lang_attributes in SUPPORTED_LANGUAGES.items():
        query_formatted = query.format(lang_attributes['dependencies_file'])

        payload = {'query': query_formatted,
                   'variables': variables}

        header = {'Authorization': 'Bearer ' + token}

        res = requests.post(GITHUB_GRAPHQL_URL, headers=header, data=json.dumps(payload))

        combined_nodes[language] = res.json()['data']['user']['repositories']['nodes']

    return combined_nodes


def javascript_dependencies_name_to_purl(dependencies):
    """
    Convert Javascript dependency names to the universal Package URL (PURL) format
    :param dependencies: Array of name@version like names
    """

    purl_dependencies = []

    for name, version in dependencies.items():
        # Remove ~ and ^ from versions
        clean_version = version.strip('~').strip('^')

        purl_dependencies.append(f'pkg:npm/{name}@{clean_version}')

    return purl_dependencies


def python_dependencies_name_to_purl(dependencies):
    """
    Convert Python dependencies names to the universal Package URL (PURL) format
    :param dependencies: List of name straight from requirements text file
    """

    purl_dependencies = []

    for dependency in dependencies.split('\n'):

        # Filter out empty lines and comments
        if not dependency or dependency.strip().startswith('#'):
            continue

        # Parse using 3rd party function
        try:
            parsed = list(requirements.parse(dependency))[0]
        except Exception as e:
            print('Error occurred while parsing Python dependency', e)
            continue

        name = parsed.name

        clean_version = None
        if parsed.specs:
            for spec in parsed.specs:
                # check the specifier (e.g. >=, <) and grabs first one with equal meaning it's legal version allowed
                if '=' in spec[0]:
                    clean_version = spec[1]  # this is the version which is idx 1 in the tuple
                    break

        purl_dependencies.append(f'pkg:pypi/{name}')

        if clean_version:
            purl_dependencies[-1] += f'@{clean_version}'

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

    all_parsed_dependencies = list()
    res_to_use_for_brach_fetch = None

    for language in SUPPORTED_LANGUAGES.keys():
        # Create expression with branch name in it
        expression = f"{branch_name}:{SUPPORTED_LANGUAGES[language]['dependencies_file']}"

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

        # Skip if no dependencies (i.e searching for requirements.txt in JS type of repo)
        if not res.json()['data']['repository']['object']:
            continue

        # Fetch the text that contains the package.json inner text
        text_response = res.json()['data']['repository']['object']['text']

        all_parsed_dependencies += parse_dependencies(text_response, language)

        # Keep assigning, to use just ones
        res_to_use_for_brach_fetch = res

    # Fetch branch names
    branch_names = [x['name'] for x in res_to_use_for_brach_fetch.json()['data']['repository']['refs']['nodes']]

    return all_parsed_dependencies, branch_names, language


def parse_dependencies(text_response, language):
    """
    Take a stringified package.json file and extract its dependencies
    :param text_reponse: A stringified package.json object
    :param language: Language for which dependencies are for
    :return:
    """

    if language == JAVASCRIPT:
        # Parse text into JSON to allow further manipulations
        text_response_json = json.loads(text_response)

        # Return only if dependencies are found
        if text_response_json.get('dependencies'):
            # Fetch the dependencies and convert into P-URLs pkg:npm/scope/name@version
            return javascript_dependencies_name_to_purl(text_response_json['dependencies'])

    elif language == PYTHON:
        return python_dependencies_name_to_purl(text_response)

    return []
