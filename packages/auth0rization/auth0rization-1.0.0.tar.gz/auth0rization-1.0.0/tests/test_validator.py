import copy
import json
import time
import unittest

from unittest.mock import patch
from jwcrypto import jwk, jwt
from auth0rization import Access, Validator
from auth0rization.errors import Auth0rizationException
from .requests_mock import RequestsMock

@patch("requests.get", RequestsMock.get)
class TestValidator(unittest.TestCase):
   _EXAMPLE_ACCESS_TOKEN = "FAKE"
   _EXAMPLE_DOMAIN = "example.fake.auth0.com"
   _EXAMPLE_AUD    = "https://api.example.com/"
   _EXAMPLE_AUD2   = "https://api2.example.com/"
   _EXAMPLE_KID    = "key_id"
   _EXAMPLE_SUB    = "sub|345llkjh345l3"
   _EXAMPLE_AZP    = "KLJsfFD8903kdfja326"


   @classmethod
   def setUpClass(cls):
      # Create key
      key = jwk.JWK.generate(kty="RSA", size=2048, kid=TestValidator._EXAMPLE_KID, alg="RSA256")
      key2 = jwk.JWK.generate(kty="RSA", size=2048, kid=TestValidator._EXAMPLE_KID, alg="RSA256")
      cls._private_key = key.export(private_key=True, as_dict=True)
      cls._public_key = key.export(private_key=False, as_dict=True)
      cls._bad_public_key = key2.export(private_key=False, as_dict=True)

      # Create keys for mocking
      cls._keys = {"keys":[cls._public_key]}
      cls._no_keys = {"keys":[]}
      cls._bad_keys = {"keys":[cls._bad_public_key]}

      # Create valid base JWT payload
      iat = int(time.time())
      exp = iat + 86400 # Expire in a day
      header = {
         "alg":"RS256",
         "typ":"JWT",
         "kid":TestValidator._EXAMPLE_KID
      }
      claims = {
         "iss":f"https://{TestValidator._EXAMPLE_DOMAIN}/",
         "sub":TestValidator._EXAMPLE_SUB,
         "aud":[
            TestValidator._EXAMPLE_AUD,
            f"https://{TestValidator._EXAMPLE_DOMAIN}/userinfo"],
         "iat":iat,
         "exp":exp,
         "azp":TestValidator._EXAMPLE_AZP,
         "scope":"openid read:good_scope",
      }

      # Create valid access token
      token = jwt.JWT(header=copy.deepcopy(header),claims=copy.deepcopy(claims))
      token.make_signed_token(key)
      cls._valid_access_token = token.serialize()

      # Create invalid access token (expired)
      mod_claims = copy.deepcopy(claims)
      mod_claims["exp"] = iat - 86400
      token = jwt.JWT(header=copy.deepcopy(header),claims=mod_claims)
      token.make_signed_token(key)
      cls._expired_access_token = token.serialize()

      # Create invalid access token (missing claim)
      mod_claims = copy.deepcopy(claims)
      del mod_claims["exp"]
      token = jwt.JWT(header=copy.deepcopy(header),claims=mod_claims)
      token.make_signed_token(key)
      cls._missing_claim_access_token = token.serialize()

      # Create invalid access token (invalid value)
      mod_claims = copy.deepcopy(claims)
      mod_claims["exp"] = "five o'clock somewhere"
      token = jwt.JWT(header=copy.deepcopy(header),claims=mod_claims)
      token.make_signed_token(key)
      cls._invalid_format_access_token = token.serialize()


   def setUp(self):
      RequestsMock.clear()


   def test__validate__expect__success_without_scope(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act
      access = auth.validate(self._valid_access_token)

      # Assert
      self.assertIsInstance(access, Access, "validate did not return instance of Access")


   def test__validate__expect__success_with_scope(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act
      access = auth.validate(self._valid_access_token, scope="read:good_scope")

      # Assert
      self.assertIsInstance(access, Access, "validate did not return instance of Access")


   def test__validate__expect__bad_scope(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._valid_access_token, scope="read:bad_scope")


   def test__validate__expect__expired(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._expired_access_token)


   def test__validate__expect__bad_audience(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD2,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._valid_access_token)


   def test__validate__expect__missing_claim(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._missing_claim_access_token)


   def test__validate__expect__missing_key(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._no_keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._valid_access_token)


   def test__validate__expect__invalid_value(self):
      # Assign
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps({}))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._valid_access_token)


   def test__validate__expect__bad_key(self):
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._bad_keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._valid_access_token)


   def test__validate__expect__invalid_claim_value(self):
      RequestsMock.register(
         "https://example.fake.auth0.com/.well-known/jwks.json",
         json.dumps(self._keys))
      auth = Validator(
         domain=TestValidator._EXAMPLE_DOMAIN,
         audience=TestValidator._EXAMPLE_AUD,
      )

      # Act / Assert Exception
      with self.assertRaises(Auth0rizationException):
         auth.validate(self._invalid_format_access_token)
