from jwcrypto import jwt
from jwcrypto.common import JWException
from .access import Access
from .errors import Auth0rizationException
from .keyset import Keyset
from .common import json_decode

class Validator:
   def __init__(self, domain, audience):
      self._domain = domain
      self._audience = audience
      self._keys = Keyset(self._domain, 300, 43200)


   @property
   def domain(self):
      return self._domain


   @property
   def audience(self):
      return self._audience


   def validate(self, access_token, scope="") -> Access:
      try:
         verified_access_token = jwt.JWT(
            key=self._keys.get(),
            jwt=access_token,
            default_claims={
               "nbf":None
            },
            check_claims={
               "iss":f"https://{self.domain}/",
               "exp":None,
               "nbf":None,
            },
         )

         access = Access(
            self.domain,
            access_token,
            json_decode(verified_access_token.claims),
         )

         access.has_scope(scope)
         access.has_audience(self.audience)

         return access
      except jwt.JWTMissingKey as error:
         self._keys.refresh()
         raise Auth0rizationException from error
      except JWException as error:
         raise Auth0rizationException from error
