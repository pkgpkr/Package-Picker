# Create your tests here.
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

from ..views import index


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def prep_request_and_call_method(self, path):
        # Create an instance of a GET request.
        request = self.factory.get(path)
        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)


    def test_index(self):
        self.prep_request_and_call_method('/')

    def test_about(self):
        self.prep_request_and_call_method('/about')

    def test_login(self):
        self.prep_request_and_call_method('/login')


    def test_callback(self):
        self.prep_request_and_call_method('/callback')


    def test_ilogout(self):
        self.prep_request_and_call_method('/logout')


    def test_repositories(self):
        self.prep_request_and_call_method('/repositories')

    def test_recommendations(self):
         #, name
        pass
