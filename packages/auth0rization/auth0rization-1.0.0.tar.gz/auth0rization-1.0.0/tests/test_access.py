import json
import unittest

from unittest.mock import patch
from auth0rization import Access
from auth0rization.errors import HttpErrorCode, Malformed
from .requests_mock import RequestsMock

@patch("requests.get", RequestsMock.get)
class TestAccess(unittest.TestCase):
   _EXAMPLE_DOMAIN = "example.fake.auth0.com"

   def test__subject__expect__equal(self):
      # Assign
      expected_subject = "sub_value"
      access = Access(None, None, {"sub":expected_subject})

      #Act
      result = access.subject

      # Assert
      self.assertEqual(result, expected_subject)


   def test__user_profile__expect__profile(self):
      # Assign
      access_token = "abc123"
      profile = json.dumps({"email":"email@example.com", "email_verified": False})
      RequestsMock.register(
         url="https://example.fake.auth0.com/userinfo",
         content=profile,
         required_headers={"Authorization": f"Bearer {access_token}"})
      access = Access(
         domain=self._EXAMPLE_DOMAIN,
         access_token=access_token,
         claims={"aud":[f"https://{self._EXAMPLE_DOMAIN}/"], "scope":"openid"})

      # Act
      result = access.user_profile()

      # Assert
      self.assertEqual(json.dumps(result), profile)


   def test__user_profile__expect__response_error(self):
      # Assign
      access_token = "abc123"
      RequestsMock.register(
         url="https://example.fake.auth0.com/userinfo",
         content={},
         required_headers={"Authorization": ""})
      access = Access(
         domain=self._EXAMPLE_DOMAIN,
         access_token=access_token,
         claims={"aud":[f"https://{self._EXAMPLE_DOMAIN}/"], "scope":"openid"})

      # Act / Assert Exception
      with self.assertRaises(HttpErrorCode):
         access.user_profile()


   def test__user_profile__expect__malformed_request(self):
      # Assign
      profile = "bad response"
      access_token = "abc123"
      RequestsMock.register(
         url="https://example.fake.auth0.com/userinfo",
         content=profile,
         required_headers={"Authorization": f"Bearer {access_token}"})
      access = Access(
         domain=self._EXAMPLE_DOMAIN,
         access_token=access_token,
         claims={"aud":[f"https://{self._EXAMPLE_DOMAIN}/"], "scope":"openid"})

      # Act / Assert Exception
      with self.assertRaises(Malformed):
         access.user_profile()
