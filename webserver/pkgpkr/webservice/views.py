from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import requests
import urllib.parse
import json

from webservice.github_util import parse_dependencies
from . import github_util
from .recommender_service import RecommenderService

from pkgpkr.settings import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, \
    GITHUB_OATH_AUTH_PATH, GITHUB_OATH_ACCESS_TOKEN_PATH

# Instantiate service class
recommender_service = RecommenderService()


def index(request):
    """ Return landing page"""
    return render(request, "webservice/index.html", {})


def about(request):
    """ Return about info"""
    return render(request, "webservice/about.html")


def login(request):
    """ Log user in using Github OAuth"""

    # Create keys if not yet there
    if not request.session.get('github_token'):
        request.session['github_token'] = None  # To keep API token
        request.session['github_info'] = None  # To keep user infor (e.g. name, avatar url)

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
        dateTime = repo['updatedAt']

        # Convert time format e.g. 2020-03-16T13:03:34Z -> 2020-03-16 13:03:34
        date = dateTime.split('T')[0]
        time = dateTime.split('T')[-1][:-1]

        repo['date'] = f'{date} {time}'

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


def recommendations(request, name):
    """
    Get recomended pacakges for the repo
    :param request:
    :param name: repo name
    :return:
    """
    # Assure login
    if not request.session.get('github_token'):
        return HttpResponseRedirect(reverse("index"))

    # Convert encoded URL back to string e.g. hello%2world -> hello/world
    name = urllib.parse.unquote_plus(name)

    # Get depencies for current repo
    dependencies = github_util.get_dependencies(request.session['github_token'], name)

    # Get predicitons
    recommended_dependencies = recommender_service.get_recommendations(dependencies)

    return render(request, "webservice/recommendations.html", {
        'repository_name': name,
        'recommendations': recommended_dependencies
    })


def reimport_model(request):
    """
    Reimport model from storage (when API is called e.g. by lambda)
    :param request:
    :return:
    """
    recommender_service.import_model()
