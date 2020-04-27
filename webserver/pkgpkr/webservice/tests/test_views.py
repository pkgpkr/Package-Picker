"""
Test the Django views
"""

import os

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from webservice import github_util
from webservice.views import index, about, login, callback, logout, repositories, recommendations

class SimpleTest(TestCase):
    """
    Tests for the Django views
    """

    def setUp(self):
        """
        Preapares request factory for every test
        :return: Nothing
        """
        self.factory = RequestFactory()

    def prep_not_github_auth_request(self, path):
        """
        Prepares request without Github authentication in session
        :param path: Path to which request will be sent
        :return: Request to pass to views function
        """
        # Create an instance of a GET request.
        request = self.factory.get(path)
        request.user = AnonymousUser()
        request.session = dict()
        return request

    def prep_with_github_auth_request(self, path):
        """
        Prepares request with Github authentication in session already
        :param path: Path to which request will be sent
        :return: Request to pass to views function
        """
        # Create an instance of a GET request.
        request = self.factory.get(path)
        request.user = AnonymousUser()

        # Set session tokean
        request.session = dict()
        request.session['github_token'] = os.environ.get('GH_TOKEN')
        request.session['github_info'] = github_util.get_user_info(request.session['github_token'])
        return request

    def call_method_and_assert(self, request, method, exp_status_code=200):
        """
        Calls method supplied and evaluate response code
        :param request: Request object prepared for this evaluation
        :param method: Methdo in views to call
        :param exp_status_code: Expected status code
        :return: Response, in case more evaluation are needed (e.g. on Url)
        """
        response = method(request)
        self.assertEqual(response.status_code, exp_status_code)
        return response

    def test_index(self):
        """
        Try fetching the home page
        """

        # Test success
        request = self.prep_not_github_auth_request('/')
        self.call_method_and_assert(request, index)

    def test_about(self):
        """
        Try fetching the about page
        """

        # Test success
        request = self.prep_not_github_auth_request('/about')
        self.call_method_and_assert(request, about)

    def test_login(self):
        """
        Try logging in
        """

        # Test proper redirect at normal functionality
        os.environ['SELENIUM_TEST'] = ''
        request = self.prep_not_github_auth_request('/login')
        response = self.call_method_and_assert(request, login, 302)
        self.assertIn('https://github.com/login/oauth/authorize?', response.url)

        # Test bypassing feature for Selenium
        os.environ['SELENIUM_TEST'] = '1'
        request = self.prep_with_github_auth_request('/login')
        response = self.call_method_and_assert(request, login, 302)
        self.assertEqual('/', response.url)

    def test_callback(self):
        """
        Make sure the login callback works
        """

        # Test Exception thrown
        request = self.prep_not_github_auth_request('/callback')
        self.assertRaises(KeyError, self.call_method_and_assert, request, callback)

    def test_logout(self):
        """
        Try to logout
        """

        # Test redirect
        request = self.prep_not_github_auth_request('/logout')
        self.call_method_and_assert(request, logout, 302)

    def test_repositories(self):
        """
        Try to view the repositories page
        """

        # Test redirect
        request = self.prep_not_github_auth_request('/repositories')
        self.call_method_and_assert(request, repositories, 302)

        # Test success
        request = self.prep_with_github_auth_request('/repositories')
        self.call_method_and_assert(request, repositories, 200)

    def test_recommendations(self):
        """
        Try to view the recommendations page
        """

        # Test redirect
        request = self.prep_not_github_auth_request('/repositories')
        response = recommendations(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 302)

        # Test success
        request = self.prep_with_github_auth_request('/repositories')
        response = recommendations(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 200)
