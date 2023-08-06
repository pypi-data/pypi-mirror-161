import json
import requests

from .errors import Malformed, HttpErrorCode, ConnectionFailed

def json_decode(data):
   try:
      return json.loads(data)
   except json.decoder.JSONDecodeError as error:
      raise Malformed from error


def get_url(url, headers=None):
   try:
      headers = {} if headers is None else headers
      response = requests.get(url, headers=headers)
      response.raise_for_status()
      return response.content
   except requests.exceptions.HTTPError as error:
      raise HttpErrorCode from error
   except requests.exceptions.ConnectionError as error:
      raise ConnectionFailed from error
