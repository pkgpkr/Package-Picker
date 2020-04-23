"""
Views for the web service
"""

import os
import urllib.parse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import requests

from webservice.github_util import parse_dependencies
from pkgpkr.settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, \
    GITHUB_OATH_AUTH_PATH, GITHUB_OATH_ACCESS_TOKEN_PATH
from . import github_util
from .recommender_service import RecommenderService

# Instantiate service class
RECOMMENDER_SERVICE = RecommenderService()

MANUAL_ENTRY_REPO_NAME = 'MANUAL'


def index(request):
    """ Return landing page"""
    return render(request, "webservice/index.html", {})


def about(request):
    """ Return about info"""
    return render(request, "webservice/about.html")


def login(request):
    """ Log user in using Github OAuth"""

    # Create keys if not yet there!
    if not request.session.get('github_token'):
        request.session['github_token'] = None  # To keep API token
        request.session['github_info'] = None  # To keep user infor (e.g. name, avatar url)

    # For Selenium testing
    if os.environ.get('SELENIUM_TEST'):
        request.session['github_token'] = os.environ.get('GH_TOKEN')
        request.session['github_info'] = github_util.get_user_info(request.session['github_token'])

        return HttpResponseRedirect(reverse('index'))

    # Redirect to attempt Github Auth
    return HttpResponseRedirect(GITHUB_OATH_AUTH_PATH)


def callback(request):
    """ Github redirect here, then retrieves token for API """

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
    """ Logs user out but keep authorization ot OAuth Github"""
    # Flush the session
    request.session['github_token'] = None
    request.session['github_info'] = None

    return HttpResponseRedirect(reverse("index"))


def repositories(request):
    """ Get full list (up to 100) for the current user """
    # Assure login
    if not request.session.get('github_token'):
        return HttpResponseRedirect(reverse("index"))

    # Get all repos
    repos = github_util.get_repositories(request.session['github_token'])

    # To track if any useful repos at all
    one_or_more_with_dependencies = False

    for repo in repos:
        # Updated Date
        date_time = repo['updatedAt']

        # Convert time format e.g. 2020-03-16T13:03:34Z -> 2020-03-16
        date = date_time.split('T')[0]

        repo['date'] = date

        # Convert string to encoded URL e.g. hello/world -> hello%2world
        repo['nameWithOwnerEscaped'] = urllib.parse.quote_plus(repo['nameWithOwner'])

        repo['dependencies'] = None

        # Check if repo has package.json
        if repo['object']:

            # Get dependencies if any
            repo['dependencies'] = parse_dependencies(repo['object']['text'])

            # Note if at least some dependencies found
            if repo['dependencies']:
                one_or_more_with_dependencies = True

    return render(request, "webservice/repositories.html", {
        'repos': repos,
        'one_or_more_with_dependencies': one_or_more_with_dependencies
    })

def manual_input(request):

    if request.method == 'POST':
        dependencies_muliline = request.POST.get('dependencies')

        dependencies = f'{{ "dependencies" : {{ {dependencies_muliline} }} }}'
        print(dependencies)
        # dependencies_list = dependencies_muliline.splitlines()
        #
        #
        # dependencies = {}
        # for d in dependencies_list:
        #
        #     # Remove whitespace and commas, split into left : right by colon
        #     d = d.strip().strip(',').split(':')
        #
        #     # Add to list of dictionaries
        #     dependencies[d[0]] = d[1]

        request.session['dependencies'] = dependencies



        return HttpResponseRedirect(reverse('recommendations', args= (MANUAL_ENTRY_REPO_NAME,)))

    return render(request, "webservice/manual-input.html", {})



def recommendations(request, name):
    """
    Get recomended pacakges for the repo
    :param request:
    :param name: repo name
    :return:
    """

    branch_name = None
    branch_names = None

    # Convert encoded URL back to string e.g. hello%2world -> hello/world
    repo_name = urllib.parse.unquote_plus(name)

    if name == MANUAL_ENTRY_REPO_NAME:
        dependencies_dict = request.session.get('dependencies')

        dependencies = github_util.parse_dependencies(dependencies_dict)


    else:
        # Assure login
        if not request.session.get('github_token'):
            return HttpResponseRedirect(reverse("index"))

        # Fetch branch name out of HTTP GET Param
        branch_name = request.GET.get('branch', default='master')

        # Get depencies for current repo, and branch names for the repo
        dependencies, branch_names = github_util.get_dependencies(request.session['github_token'],
                                                                  repo_name,
                                                                  branch_name)

    # Get predicitons
    recommended_dependencies = RECOMMENDER_SERVICE.get_recommendations(dependencies)

    return render(request, "webservice/recommendations.html", {
        'repository_name': repo_name,
        'recommendations': recommended_dependencies,
        'branch_names': branch_names,
        'current_branch': branch_name
    })
