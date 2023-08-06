# auth0rization

A library to provide simple methods to validate and use Auth0 JWT tokens.


## Installation
```
pip install auth0rization
```

## Example usage
```
import json
import auth0rization

access_token = "<access_token>"

validator = auth0rization.Validator(
   domain="<auth0_domain>",
   audience="<audience>"
)

access = validator.validate(access_token, "read:example")

profile = access.user_profile()

print(json.dumps(profile, indent=2))
```