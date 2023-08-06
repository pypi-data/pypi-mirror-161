import time
from jwcrypto import jwk
from jwcrypto.common import JWException
from .errors import Auth0rizationException
from .common import get_url

class Keyset:
   def __init__(self, domain, min_ttl, max_ttl):
      self._domain = domain
      self._min_ttl = min_ttl
      self._max_ttl = max_ttl
      self._last_update = -1
      self._next_update = -1
      self._key_set = None


   def get(self) -> jwk.JWKSet:
      self._update()
      return self._key_set


   def refresh(self) -> None:
      self._next_update = self._last_update + self._min_ttl


   def _update(self) -> None:
      current_time = time.time()
      if self._last_update < 0  or current_time > self._next_update:
         data = get_url(f"https://{self._domain}/.well-known/jwks.json")
         try:
            self._key_set = jwk.JWKSet.from_json(data)
         except JWException as error:
            raise Auth0rizationException from error
         finally:
            self._last_update = current_time
            self._next_update = current_time + self._max_ttl
