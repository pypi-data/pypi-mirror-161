import json
import unittest
from unittest.mock import patch
from jwcrypto import jwk
import auth0rization
from .requests_mock import RequestsMock
from .time_mock import TimeMock

@patch("requests.get", RequestsMock.get)
@patch("time.time", TimeMock.time)
class TestKeyset(unittest.TestCase):
   _EXAMPLE_DOMAIN = "example.fake.auth0.com"

   @classmethod
   def setUpClass(cls):
      # Create key
      key = jwk.JWK.generate(kty="RSA", size=2048, kid='example_kid', alg="RSA256")
      cls._public_key = key.export(private_key=False, as_dict=True)
      # Create keys for mocking
      cls._keys = {"keys":[cls._public_key]}
      cls._keys_str = json.dumps(cls._keys)


   def setUp(self):
      TimeMock.set_time(0)
      RequestsMock.clear()
      RequestsMock.register(
         f"https://{self._EXAMPLE_DOMAIN}/.well-known/jwks.json",
         self._keys_str)


   def test__key_set__expect__key_set(self):
      # Assign
      keys = auth0rization.Keyset(self._EXAMPLE_DOMAIN, 300, 43200)

      # Act
      result = keys.get()

      # Assert
      self.assertEqual(result, jwk.JWKSet.from_json(self._keys_str))


   def test__key_set__expect__key_set_once(self):
      # Assign
      keys = auth0rization.Keyset(self._EXAMPLE_DOMAIN, 300, 43200)

      # Act
      keys.get()
      TimeMock.set_time(43200)
      result = keys.get()

      # Assert
      self.assertEqual(result, jwk.JWKSet.from_json(self._keys_str))
      self.assertEqual(
         RequestsMock.call_count(
            f"https://{self._EXAMPLE_DOMAIN}/.well-known/jwks.json"),
            1,
            "Keyset endpoint called more than once.")


   def test__key_set__expect__bad_key_set(self):
      # Assign
      RequestsMock.register(
         f"https://{self._EXAMPLE_DOMAIN}/.well-known/jwks.json",
         "")
      keys = auth0rization.Keyset(self._EXAMPLE_DOMAIN, 300, 43200)

      # Act / Assert Exception
      with self.assertRaises(auth0rization.errors.Auth0rizationException):
         keys.get()


   def test__key_set__expect__expired(self):
      # Assign
      keys = auth0rization.Keyset(self._EXAMPLE_DOMAIN, 300, 43200)

      # Act
      keys.get()
      TimeMock.set_time(43201)
      result = keys.get()

      # Assert
      self.assertEqual(result, jwk.JWKSet.from_json(self._keys_str))
      self.assertEqual(
         RequestsMock.call_count(
            f"https://{self._EXAMPLE_DOMAIN}/.well-known/jwks.json"),
            2,
            "Keyset endpoint not called twice.")


   def test__refresh__expect__refresh_not_expired(self):
      # Assign
      keys = auth0rization.Keyset(self._EXAMPLE_DOMAIN, 300, 43200)

      # Act
      keys.get()
      keys.refresh()
      TimeMock.set_time(300)
      result = keys.get()

      # Assert
      self.assertEqual(result, jwk.JWKSet.from_json(self._keys_str))
      self.assertEqual(
         RequestsMock.call_count(
            f"https://{self._EXAMPLE_DOMAIN}/.well-known/jwks.json"),
            1,
            "Keyset endpoint called more than once.")


   def test__refresh__expect__refresh_expired(self):
      # Assign
      keys = auth0rization.Keyset(self._EXAMPLE_DOMAIN, 300, 43200)

      # Act
      keys.get()
      keys.refresh()
      TimeMock.set_time(301)
      result = keys.get()

      # Assert
      self.assertEqual(result, jwk.JWKSet.from_json(self._keys_str))
      self.assertEqual(
         RequestsMock.call_count(
            f"https://{self._EXAMPLE_DOMAIN}/.well-known/jwks.json"),
            2,
            "Keyset endpoint not called twice.")
