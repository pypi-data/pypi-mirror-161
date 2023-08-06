from .errors import Auth0rizationException
from .common import get_url, json_decode

class Access:
   def __init__(self, domain, access_token, claims):
      self._domain = domain
      self._access_token = access_token
      self._audience = claims.get("aud", [])
      self._scope = claims.get("scope", None)
      self._subject = claims.get("sub", None)


   @property
   def domain(self):
      return self._domain


   @property
   def access_token(self):
      return self._access_token


   @property
   def scope(self):
      return self._scope


   @property
   def audience(self):
      return self._audience


   @property
   def subject(self):
      return self._subject


   def user_profile(self):
      self.has_audience(f"https://{self.domain}/")
      self.has_scope("openid")
      raw_profile = get_url(
         url=f"https://{self.domain}/userinfo",
         headers={
            "Authorization": f"Bearer {self.access_token}",
         })

      return json_decode(raw_profile)


   def has_scope(self, scope: str) -> None:
      scope_from_claim = self.scope.split()
      expected_scope = str(scope).split()
      if not all(scope in scope_from_claim for scope in expected_scope):
         raise Auth0rizationException


   def has_audience(self, audience: str) -> None:
      if audience not in self.audience:
         raise Auth0rizationException
