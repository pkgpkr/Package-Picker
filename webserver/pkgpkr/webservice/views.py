"""
Views for the web service
"""

import os
import json
import urllib.parse

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.http import HttpResponse
from django.urls import reverse

import requests
from django.views.decorators.csrf import csrf_exempt

from webservice.github_util import parse_dependencies
from pkgpkr.settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, \
    GITHUB_OATH_AUTH_PATH, GITHUB_OATH_ACCESS_TOKEN_PATH, JAVASCRIPT, PYTHON, SUPPORTED_LANGUAGES, \
    DEFAULT_MAX_RECOMMENDATIONS
from . import github_util
from .recommender_service import RecommenderService

# Instantiate service class
RECOMMENDER_SERVICE = RecommenderService()

DEMO_REPO_INPUT_NAME = 'DEMO'


def index(request):
    """
    Return landing page

    arguments:
        :request: GET HTTP request

    returns:
        Rendered home (index) page
    """
    return render(request,
                  "webservice/index.html",
                  {'demo_input_repo_name': DEMO_REPO_INPUT_NAME,
                   'supported_languages': sorted([lang.capitalize() for lang in SUPPORTED_LANGUAGES.keys()])})


def about(request):
    """
    Return about info

    arguments:
        :request: GET HTTP request

    returns:
        Rendered about page
    """
    return render(request, "webservice/about.html")


def login(request):
    """ Log user in using Github OAuth

    arguments:
        :request: GET HTTP request

    returns:
        Redirects to index
    """

    # Create keys if not yet there!
    if not request.session.get('github_token'):
        request.session['github_token'] = None  # To keep API token
        request.session['github_info'] = None  # To keep user infor (e.g. name, avatar url)

    # For Selenium testing
    if os.environ.get('SELENIUM_TEST') == '1':
        assert os.environ.get('GH_TOKEN'), "GH_TOKEN not set"
        request.session['github_token'] = os.environ.get('GH_TOKEN')
        request.session['github_info'] = github_util.get_user_info(request.session['github_token'])

        return HttpResponseRedirect(reverse('index'))

    # Redirect to attempt Github Auth
    return HttpResponseRedirect(GITHUB_OATH_AUTH_PATH)


def callback(request):
    """
    Github redirect here, then retrieves token for API

    arguments:
        :request: GET HTTP request

    returns:
        Redirects to  index
    """
    # Get code supplied by github
    code = request.GET.get('code')

    # Payload to fetch
    payload = {'client_id': GITHUB_CLIENT_ID,
               'client_secret': GITHUB_CLIENT_SECRET,
               'code': code}

    headers = {"accept": "application/json"}

    # Call github to get token
    res = requests.post(GITHUB_OATH_ACCESS_TOKEN_PATH,
                        data=payload,
                        headers=headers)

    # Set token
    request.session['github_token'] = res.json()['access_token']

    # Call for user info and store in sessions (to be used for UI)
    request.session['github_info'] = github_util.get_user_info(request.session['github_token'])

    return HttpResponseRedirect(reverse('index'))


def logout(request):
    """
    Logs user out but keep authorization ot OAuth Github

    arguments:
        :request: GET HTTP request

    returns:
        Redirects to index
    """

    # Flush the session
    request.session['github_token'] = None
    request.session['github_info'] = None

    return HttpResponseRedirect(reverse("index"))


def repositories(request):
    """
    Get full list (up to 100) for the current user

    arguments:
        :request: GET HTTP request

    returns:
        Rendered repositories page
    """

    # Assure login
    if not request.session.get('github_token'):
        return HttpResponseRedirect(reverse("index"))

    # Get all repos
    repos_per_language = github_util.get_repositories(request.session['github_token'])

    combined_repos = dict()

    for language, repos in repos_per_language.items():

        for repo in repos:

            # Skip if repo has no dependencies
            if not repo['object']:
                continue

            # Updated Date
            date_time = repo['updatedAt']

            # Convert time format e.g. 2020-03-16T13:03:34Z -> 2020-03-16
            date = date_time.split('T')[0]

            repo['date'] = date

            # Convert string to encoded URL e.g. hello/world -> hello%2world
            repo['nameWithOwnerEscaped'] = urllib.parse.quote_plus(repo['nameWithOwner'])

            repo['language'] = language

            # Get dependencies if any,  remember if at least some dependencies found
            if parse_dependencies(repo['object']['text'], language, True):
                combined_repos[repo['nameWithOwner']] = repo

    return render(request, "webservice/repositories.html", {
        'repos': combined_repos.values()
    })


def recommendations(request, name):
    """
    Get recommended packages for the repo

    arguments:
        :request: GET/POST HTTP request
        :name: repo name

    returns:
        Rendered recommendation page
    """

    # Convert encoded URL back to string e.g. hello%2world -> hello/world
    repo_name = urllib.parse.unquote_plus(name)

    # Process for DEMO run
    if request.method == 'POST':
        language = request.POST.get('language')
        language = language.lower()

        dependencies = request.POST.get('dependencies')
        dependencies = dependencies.strip(',')

        if language not in SUPPORTED_LANGUAGES.keys():
            return HttpResponse(f'Demo language {language} not supported', status=404)

        request.session['dependencies'] = dependencies
        request.session['language'] = language

        branch_name = None
        branch_names = None

    # If GET it means it's not a DEMO POST call with manual dependencies inputs
    else:
        # Assure login
        if not request.session.get('github_token'):
            return HttpResponseRedirect(reverse("index"))

        # Fetch branch name out of HTTP GET Param
        branch_name = request.GET.get('branch', default='master')

        # Get branch names and language (ONLY) for the repo, no need for dependencies yet
        _, branch_names, language = github_util.get_dependencies(request.session['github_token'],
                                                                 repo_name,
                                                                 branch_name)

    return render(request, "webservice/recommendations.html", {
        'repository_name': repo_name,
        'recommendation_url': f"/recommendations/{urllib.parse.quote_plus(name)}?branch={branch_name}",
        'branch_names': branch_names,
        'current_branch': branch_name,
        'language': language
    })


def recommendations_json(request, name):
    """
    Get recommended packages for the repo in JSON format

    arguments:
        :request: GET HTTP request
        :name: repo name

    returns:
        JSON object with recommendations
    """

    # Convert encoded URL back to string e.g. hello%2world -> hello/world
    repo_name = urllib.parse.unquote_plus(name)

    if name == DEMO_REPO_INPUT_NAME:
        dependencies = github_util.parse_dependencies(request.session.get('dependencies'),
                                                      request.session.get('language'))

        # Set to none (will also allow for not showing branch selector
        branch_name = None

    else:
        if not request.session.get('github_token'):
            return HttpResponse('Unauthorized', status=401)

        # Fetch branch name out of HTTP GET Param
        branch_name = request.GET.get('branch', default='master')

        # Get dependencies for current repo, and branch names for the repo
        dependencies, _, _ = github_util.get_dependencies(request.session['github_token'],
                                                          repo_name,
                                                          branch_name)

    # Get predictions
    recommended_dependencies = RECOMMENDER_SERVICE.get_recommendations(dependencies)

    # Setup data to be returned
    data = {
        'repository_name': repo_name,
        'current_branch': branch_name,
        'data': recommended_dependencies
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


@csrf_exempt
def recommendations_service_api(request):
    """
    Returns package recommendations for API POST call without authentication

    arguments:
        :request: POST request of application/json type

    returns:
        list of package recommendations
    """
    if request.method == 'POST':

        # Fetch JSON
        try:
            json_data = json.loads(request.body)  # request.raw_post_data w/ Django < 1.4
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Could not parse JSON.")

        # Fetch non-optional keys
        try:
            dependencies = json_data['dependencies']
            language = json_data['language'].lower()
        except KeyError:
            return HttpResponseBadRequest('Required JSON keys: `dependencies`, `language`')
        except AttributeError as e:
            return HttpResponseBadRequest(f'Error casting language to lower(): {e}')

        # Assure proper inputs
        if not isinstance(dependencies, list) or not dependencies:
            return HttpResponseBadRequest(f'{language.capitalize()} dependencies must be non-empty and of type LIST (i.e. [...]).')

        # Convert comma separated dependencies into proper expected format
        if language == PYTHON:
            dependencies = '\n'.join(dependencies)
        elif language == JAVASCRIPT:
            # Converts e.g ["lodash:4.17.15","react:16.13.1"] -> '"lodash":"4.17.15","react":"16.13.1"'
            formatted_dependencies_list = ['"' + dep.replace(":", '":"') + '"' for dep in dependencies]
            dependencies = ','.join(formatted_dependencies_list)

        else:
            return HttpResponseBadRequest(f"Language not supported: [{language}].")

        # Parse dependencies
        dependencies = github_util.parse_dependencies(dependencies, language)

        # Get recommendation all or cutoff if limit specified
        if 'max_recommendations' in json_data:
            recommended_dependencies = RECOMMENDER_SERVICE.get_recommendations(dependencies,
                                                                               json_data['max_recommendations'])
        else:
            recommended_dependencies = RECOMMENDER_SERVICE.get_recommendations(dependencies)

        # Convert the output tuples into list of dictionaries with names to return back
        output_recommended_dependencies = []
        for recommended_dependency in recommended_dependencies:
            d = dict()

            d['forPackage'] = recommended_dependency[0]
            d['recommendedPackage'] = recommended_dependency[1]
            d['url'] = recommended_dependency[2]
            d['pkgpkrScore'] = recommended_dependency[3]
            d['absoluteTrendScore'] = recommended_dependency[4]
            d['relativeTrendScore'] = recommended_dependency[5]
            d['boundedPopularityScore'] = recommended_dependency[6]
            d['boundedSimilarityScore'] = recommended_dependency[7]
            d['categories'] = recommended_dependency[8]
            d['displayDate'] = recommended_dependency[9]
            d['monthlyDownloadsLastMonth'] = recommended_dependency[10]

            output_recommended_dependencies.append(d)

        # Setup data to be returned
        data = {
            'language': language,
            'recommended_dependencies': output_recommended_dependencies
        }

        return HttpResponse(json.dumps(data), content_type="application/json")

    return HttpResponseNotAllowed(['POST'])
