class Auth0rizationException(Exception):
   pass

class ResponseException(Auth0rizationException):
   pass

class HttpErrorCode(ResponseException):
   pass

class ConnectionFailed(ResponseException):
   pass

class Malformed(ResponseException):
   pass
