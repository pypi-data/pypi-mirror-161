import unittest

from unittest.mock import patch
from auth0rization.errors import ConnectionFailed, HttpErrorCode
from auth0rization.common import get_url
from .requests_mock import RequestsMock

@patch("requests.get", RequestsMock.get)
class TestUtilities(unittest.TestCase):
   _EXAMPLE_URL = "https://api.example.com/.well-known/jwks.json"

   def setUp(self):
      RequestsMock.clear()


   def test__get_url__expect__successful(self):
      # Assign
      payload = b"{\"key\":\"value\"}"
      RequestsMock.register(self._EXAMPLE_URL, payload)

      #Act
      result = get_url(TestUtilities._EXAMPLE_URL)

      # Assert
      self.assertEqual(result, payload)


   def test__get_url__expect__http_error(self):
      # Assign
      RequestsMock.register(self._EXAMPLE_URL, None, options={"force_http_error":True})

      # Act / Assert Exception
      with self.assertRaises(HttpErrorCode):
         get_url(TestUtilities._EXAMPLE_URL)


   @patch("requests.get", RequestsMock.get)
   def test__get_url__expect__connection_error(self):
      # Assign
      RequestsMock.register(self._EXAMPLE_URL, None, options={"connection_error":True})

      #Act / Assert Exception
      with self.assertRaises(ConnectionFailed):
         get_url(TestUtilities._EXAMPLE_URL)
