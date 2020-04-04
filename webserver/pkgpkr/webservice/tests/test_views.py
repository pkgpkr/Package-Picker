# Create your tests here.
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

from ..views import index, about, login, callback, logout, repositories


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def prep_request_and_call_method(self, path, method, exp_status_code=200):
        # Create an instance of a GET request.
        request = self.factory.get(path)
        request.user = AnonymousUser()
        request.session = dict()

        # Test my_view() as if it were deployed at /customer/details
        response = method(request)

        self.assertEqual(response.status_code, exp_status_code)


    def test_index(self):
        self.prep_request_and_call_method('/', index, )

    def test_about(self):
        self.prep_request_and_call_method('/about', about)

    def test_login(self):
        self.prep_request_and_call_method('/login', login, 302)
        # TODO try with proper token should not redirect

    # TODO revisit after MS2
    # def test_callback(self):
    #     self.prep_request_and_call_method('/callback', callback)

    def test_logout(self):
        self.prep_request_and_call_method('/logout', logout, 302)


    def test_repositories(self):
        self.prep_request_and_call_method('/repositories', repositories, 302)
        # TODO try with proper token should not redirect


    def test_recommendations(self):
         #, name
        pass
