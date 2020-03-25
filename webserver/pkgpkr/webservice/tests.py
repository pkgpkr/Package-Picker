from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

# Create your tests here.

from .views import index


class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get("/")
        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_vlad_bad(self):
        # TODO THIS IS DUMMY
        self.assertTrue(False)
