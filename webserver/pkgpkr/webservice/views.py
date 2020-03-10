from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
import os
import requests

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')

def index(request):
    return render(request, "webservice/index.html")


def about(request):
    return render(request, "webservice/about.html")


def login(request):

    URI = 'http://localhost:8000/callback'


    return HttpResponseRedirect(f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&allow_signup=false&redirect_uri={URI}")

    #return render(request, "webservice/login.html")



def callback(request):


    code = request.GET.get('code')

    payload = {'client_id':CLIENT_ID,
               'client_secret':CLIENT_SECRET,
               'code':code}
    headers={"accept": "application/json"}
    res = requests.post('https://github.com/login/oauth/access_token',
                        data=payload,
                        headers=headers)

    print(res)
    print(res.json())



    header = {'Authorization': 'Bearer ' + res.json()['access_token']}

    url = 'https://api.github.com/user'
    res = requests.get(url, headers=header)


    print(res)
    print(res.text)

    return render(request, "webservice/login.html")


def logout(request):
    return HttpResponseRedirect(reverse("index"))


def repositories(request):

    # TODO Fetch repos fro Github

    dummy_repos = [{'name': 'helloworld',
                    'category': 'js',
                    'donwloads': 30500,
                    'rate': 4,
                    'last_upd': '2020-02-10'},
                   {'name': 'details-dialog-entitlement',
                    'category': 'js',
                    'donwloads': 1800,
                    'rate': 5,
                    'last_upd': '2020-01-314'}]

    return render(request, "webservice/repositories.html", {
        'repositories': dummy_repos
    })



def recommendations(request, name):

    return render(request, "webservice/recommendations.html", {
        'repository_name': name
    })
