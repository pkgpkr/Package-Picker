"""
Test the Django views
"""
import json
import os

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser

from webservice import github_util
from webservice.views import index, about, login, callback, logout, repositories, recommendations, recommendations_json, \
    recommendations_service_api


class SimpleTest(TestCase):
    """
    Tests for the Django views
    """

    def setUp(self):
        """
        Preapares request factory for every test

        returns:
            A RequestFactory
        """
        self.factory = RequestFactory()

    def prep_not_github_auth_request(self, path, instantiate_user_session=True):
        """
        Prepares request without Github authentication in session

        arguments:
            :path: Path to which request will be sent
            :instantiate_user_session: If there's a need to create placeholder for user session

        returns:
            Request to pass to views function
        """
        # Create an instance of a GET request.
        request = self.factory.get(path)

        if instantiate_user_session:
            request.user = AnonymousUser()
            request.session = dict()

        return request

    def prep_with_github_auth_request(self, path):
        """
        Prepares request with Github authentication in session already

        arguments:
            :path: Path to which request will be sent

        returns:
            Request to pass to views function
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

        arguments:
            :request: Request object prepared for this evaluation
            :method: Method in views to call
            :exp_status_code: Expected status code

        returns:
            Response, in case more evaluation are needed (e.g. on Url)
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
        request = self.prep_not_github_auth_request('/repositories/pkgpkr1/express')
        response = recommendations(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 302)

        # Test success
        request = self.prep_with_github_auth_request('/repositories/pkgpkr1/express')
        response = recommendations(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 200)

        # Test bad demo language
        request = self.prep_with_github_auth_request('/repositories/pkgpkr1/DEMO')
        request.method = 'POST'
        request.POST = {
            'dependencies': '"accepts": "~1.3.7","array-flatten": "1.1.1","body-parser": "1.19.0"',
            'language': 'NOT A SUPPORTED LANGUAGE'
        }
        response = recommendations(request, 'pkgpkr1/DEMO')
        self.assertEqual(response.status_code, 404)

    def test_demo_input(self):
        # Test success
        request = self.prep_not_github_auth_request('/repositories/DEMO')
        request.method = 'POST'
        request.POST = {
            'dependencies': '"accepts": "~1.3.7","array-flatten": "1.1.1","body-parser": "1.19.0"',
            'language': 'javascript'
        }
        response = recommendations(request, 'DEMO')
        self.assertEqual(response.status_code, 200)

        # Test fail
        request = self.prep_not_github_auth_request('/repositories/DEMO')
        request.method = 'GET'
        response = recommendations(request, 'DEMO')
        self.assertEqual(response.status_code, 302)

    def test_recommendations_json(self):
        # Test fail
        request = self.prep_not_github_auth_request('/repositories/pkgpkr1/express')
        response = recommendations_json(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 401)

        # Test success
        request = self.prep_with_github_auth_request('/repositories/pkgpkr1/express')
        response = recommendations_json(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        self.assertIn('"repository_name": "pkgpkr1/express"', response.content.decode())

        # Test with branch
        request = self.prep_with_github_auth_request('/repositories/pkgpkr1/express?branch=test')
        response = recommendations_json(request, 'pkgpkr1/express')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.content)
        self.assertIn('"current_branch": "test"', response.content.decode())

    def assertion_helper_for_recom_service_api(self, post_data, expected_code, expected_message_substring):

        request = self.factory.post('/api/recommendations',
                                    data=post_data,
                                    content_type='application/json')

        response = recommendations_service_api(request)
        self.assertEqual(response.status_code, expected_code)
        self.assertIn(expected_message_substring, response.content.decode())

        return response

    def test_recommendations_service_api(self):
        # Assert Method not found
        request = self.prep_not_github_auth_request('/api/recommendations', instantiate_user_session=False)
        request.method = 'GET'
        response = recommendations_service_api(request)
        self.assertEqual(response.status_code, 405)

        ### Assert issues ###


        # Issue with json, NOTE: there's no way to pass bad JSON, so just changing content_type so it's not there
        post_data = "THIS IS NOT A JSON!"
        self.assertion_helper_for_recom_service_api(post_data, 500, 'Could not parse JSON')

        # Issue with missing keys
        post_data = {}
        self.assertion_helper_for_recom_service_api(post_data, 500, 'Required JSON key')

        # Issue with language value
        post_data = {"language": "NOT SUPPORTED VALUE", "dependencies": {}}
        self.assertion_helper_for_recom_service_api(post_data, 500, 'Language not supported')

        # Issue with language missing
        post_data = {"language": None, "dependencies": {"lodash": "4.17.15"}}
        self.assertion_helper_for_recom_service_api(post_data, 500, 'Error casting language to lower()')

        # Issue with empty dependencies for Javascript
        for dependency in [{}, None]:
            post_data = {"language": "javascript",
                         "dependencies": dependency}

            self.assertion_helper_for_recom_service_api(post_data, 500,
                                                        'Javascript dependencies must be non-empty and of type DICT')

        # Issue with empty dependencies for Python
        for dependency in [[], None]:
            post_data = {"language": "Python",
                         "dependencies": dependency}

            self.assertion_helper_for_recom_service_api(post_data, 500,
                                                        'Python dependencies must be non-empty and of type LIST')

        # Proper Javascript
        post_data = {"language": "Javascript",
                     "dependencies": {"lodash": "4.17.15", "react": "16.13.1",
                                      "express": "4.17.1", "moment": "2.24.0"}}

        response = self.assertion_helper_for_recom_service_api(post_data, 200, 'recommended_dependencies')

        self.assertGreater(len(json.loads(response.content.decode())['recommended_dependencies']), 10)

        # Proper Python
        post_data = {"language": "Python",
                     "dependencies": ["Django==2.1.2", "requests>=2.23.0", "tensorflow==2.1.0"]}

        response = self.assertion_helper_for_recom_service_api(post_data, 200, 'recommended_dependencies')

        self.assertGreater(len(json.loads(response.content.decode())['recommended_dependencies']), 10)

        # Limited Javascript
        post_data = {"language": "Javascript",
                     "dependencies": {"lodash": "4.17.15", "react": "16.13.1",
                                      "express": "4.17.1", "moment": "2.24.0"},
                     "max_recommendations": 10}

        response = self.assertion_helper_for_recom_service_api(post_data, 200, 'recommended_dependencies')

        self.assertLessEqual(len(json.loads(response.content.decode())['recommended_dependencies']), 10)

        # Limited Python
        post_data = {"language": "Python",
                     "dependencies": ["Django==2.1.2", "requests>=2.23.0", "tensorflow==2.1.0"],
                     "max_recommendations": 10}

        response = self.assertion_helper_for_recom_service_api(post_data, 200, 'recommended_dependencies')

        self.assertLessEqual(len(json.loads(response.content.decode())['recommended_dependencies']), 10)
