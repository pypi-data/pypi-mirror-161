import requests

class ResponseMock:
   def __init__(self, content, force_http_error = False, required_headers=None):
      self._content = content
      self._force_http_error = force_http_error
      self._required_headers = {}
      if required_headers is not None:
         self._required_headers = required_headers
      self._request_headers = {}


   def raise_for_status(self):
      if self._force_http_error:
         raise requests.exceptions.HTTPError

      for required_header, required_value in self._required_headers.items():
         contains = required_header in self._request_headers
         value = self._request_headers.get(required_header, None)
         if not contains or required_value != value:
            raise requests.exceptions.HTTPError


   def set_request_headers(self, headers):
      self._request_headers = headers


   @property
   def content(self):
      return self._content


class RequestsMock:
   _responses = {}

   @classmethod
   def get(cls, url, **kargs):
      response_data = cls._responses[url]

      response_data["call_count"] += 1

      if response_data.get("connection_error", False):
         raise requests.exceptions.ConnectionError

      response = response_data["response"]
      response.set_request_headers(kargs.get("headers",{}))
      return response


   @classmethod
   def register(cls, url, content, options=None, required_headers=None):
      if options is None:
         options = {}
      cls._responses[url] = {
         "response": ResponseMock(
            content,
            options.get("force_http_error", False),
            {} if required_headers is None else required_headers),
         "connection_error": options.get("connection_error", False),
         "call_count": 0,
      }


   @classmethod
   def call_count(cls, url):
      return cls._responses[url]["call_count"]


   @classmethod
   def clear(cls):
      cls._responses.clear()
