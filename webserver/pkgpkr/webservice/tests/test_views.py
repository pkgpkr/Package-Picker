# Create your tests here.
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

from webservice import github_util
from ..views import index, about, login, callback, logout, repositories

import os

class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()


    def prep_not_githib_auth_request(self, path):
        # Create an instance of a GET request.
        request = self.factory.get(path)
        request.user = AnonymousUser()
        request.session = dict()
        return request



    def prep_with_githib_auth_request(self, path):
        # Create an instance of a GET request.
        request = self.factory.get(path)
        request.user = AnonymousUser()
        request.session = dict()
        request.session['github_token'] = os.environ.get('TOKEN')
        request.session['github_info'] = github_util.get_user_info(request.session['github_token'])
        return request


    def prep_request_and_call_method(self, request, method, exp_status_code=200):


        # Test my_view() as if it were deployed at /customer/details
        response = method(request)

        self.assertEqual(response.status_code, exp_status_code)


    def test_index(self):
        request = self.prep_not_githib_auth_request('/')
        self.prep_request_and_call_method(request, index)

    def test_about(self):
        request = self.prep_not_githib_auth_request('/about')
        self.prep_request_and_call_method(request, about)

    def test_login(self):
        request = self.prep_not_githib_auth_request('/login')
        self.prep_request_and_call_method(request, login, 302)

        # TODO try with proper token should not redirect

    # TODO revisit after MS2
    # def test_callback(self):
    #     self.prep_request_and_call_method('/callback', callback)

    def test_logout(self):
        request = self.prep_not_githib_auth_request('/logout')
        self.prep_request_and_call_method(request, logout, 302)


    def test_repositories(self):
        request = self.prep_not_githib_auth_request('/repositories')
        self.prep_request_and_call_method(request, repositories, 302)

        request = self.prep_with_githib_auth_request('/repositories')
        self.prep_request_and_call_method(request, repositories, 200)


        # TODO try with proper token should not redirect


    def test_recommendations(self):
         #, name
        pass
