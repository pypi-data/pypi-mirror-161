# auth-get-sso-cookie

This utility replaces `cern-get-sso-cookie` for the new SSO.

`auth-get-sso-cookie` acquires CERN Single Sign-On cookie using Kerberos credentials allowing for automated access to CERN SSO protected pages using tools alike wget, curl or similar. 

Additionally, this package includes other utilities to get access tokens for OpenID Connect and OAuth2 applications:

- `auth-get-user-token`: Get a user token by interactively signing in.

Legacy commands (unsupported):
- `auth-get-sso-token`


## Install
Run the setuptools file included with the sources:

```
pip install .
```

Alternatively, RPM builds for `auth-get-sso-cookie` can be dowloaded from the following repositories:

- CentOS 7: http://linuxsoft.cern.ch/internal/repos/authz7-stable/x86_64/os/Packages/
- CentOS Stream 8: http://linuxsoft.cern.ch/internal/repos/authz8s-stable/x86_64/os/Packages/
- CentOS 9: http://linuxsoft.cern.ch/internal/repos/authz9-stable/x86_64/os/Packages/


## Usage

You will need a valid Kerberos TGT to run the utility, e.g. run `kinit <user>` before the script.


## auth-get-sso-cookie

Use this tool to get a valid SSO and application cookie from a protected URL. This cookie will be valid for 10 hours.

**Warning:** Every time you get new cookies, this will start a new SSO session but it won't log off any other session. To avoid starting too many sessions, please reuse your cookies as much as possible while they are valid.

**This tool is NOT compatible with accounts with accounts that have "always-on 2FA"**. Please consider the following alternatives:

- For automated workflows: Two-factor authentication is not designed for this scenario. Use a service account with a single password.
- For user authentication in a command line interface: Migrate your service to OAuth2/OIDC to accept bearer tokens and use `auth-get-user-token`. You can also use Kerberos authentication.


```
$ auth-get-sso-cookie --help
usage: auth-get-sso-cookie [-h] [-u URL] [-o OUTFILE] [--nocertverify]
                              [--verbose] [--debug]

Acquires the CERN Single Sign-On cookie using Kerberos credentials

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     CERN SSO protected site URL to get cookie for.
  -o OUTFILE, --outfile OUTFILE
                        File to store the cookie for further usage
  --nocertverify        Disables peer certificate verification. Useful for
                        debugging/tests when peer host does have a self-signed
                        certificate for example.
  --verbose, -v         Provide more information on authentication process
  --debug, -vv          Provide detailed debugging information
```


```
auth-get-sso-cookie -u <url> -o <cookies_file>
```

Example: 
```bash
auth-get-sso-cookie -u https://openstack.cern.ch -o cookies.txt
curl -L -b cookies.txt https://openstack.cern.ch
```


## auth-get-user-token

Use this tool to get a valid SSO token for a client that accepts Device Authorization Grant. The obtained token will be valid for 20 minutes.

If you need longer sessions (up to 12 hours), don't use the `-x` option and use the `refresh_token` from the response to renew your tokens as in the last example below.

```
$ auth-get-user-token --help
usage: auth-get-user-token [-h] [--clientid CLIENTID] [--auth-realm AUTH_REALM] [--extract-token] [-o OUTFILE] [-a AUDIENCE] [--nocertverify] [--verbose] [--debug]
                           [--auth-server AUTH_SERVER]

Acquires a user token using device authorization grant. It does not require any local credentials.

options:
  -h, --help            show this help message and exit
  --clientid CLIENTID, -c CLIENTID
                        Client ID of a public client with device authorization grant enabled
  --auth-realm AUTH_REALM, -r AUTH_REALM
                        Authentication realm (default: cern)
  --extract-token, -x   Extract and save only the access token instead of the full response json
  -o OUTFILE, --outfile OUTFILE
                        File to store the token for further usage
  -a AUDIENCE, --audience AUDIENCE
                        Exchange token for another target audience or client ID
  --nocertverify        Disables peer certificate verification. Useful for debugging/tests when peer host does have a self-signed certificate for example.
  --verbose, -v         Provide more information on authentication process
  --debug, -vv          Provide detailed debugging information
  --auth-server AUTH_SERVER, -s AUTH_SERVER
                        Authentication server (default: auth.cern.ch)
```

One-time usage example:

```bash
auth-get-user-token -c device-code-flow-test -o token.txt -x
token=$(<token.txt)
curl -X PUT "https://myapi.cern.ch/api/foobar" -H  "authorization: Bearer $token" -d "{\"foo\": \"bar\"}"
```

Example with a longer lasting session (requires `jq`):

```bash
# Authenticate user and get the initial access token
auth-get-user-token -c device-code-flow-test -o token.txt
refresh_token=$(cat token.txt | jq -r .refresh_token)
access_token=$(cat token.txt | jq -r .access_token)

# Call something using the token
curl -X PUT "https://myapi.cern.ch/api/foobar" -H  "authorization: Bearer $access_token" -d "{\"foo\": \"bar\"}"

# Get a new valid token any time, even after the initial access token expires
new_token=$(curl -X POST "https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token" -d "grant_type=refresh_token" -d "refresh_token=$refresh_token" -d "client_id=device-code-flow-test")
refresh_token=$(echo $new_token | jq -r .refresh_token)
access_token=$(echo $new_token | jq -r .access_token)

# Use the new token to make more requests
curl -X PUT "https://myapi.cern.ch/api/foobar" -H  "authorization: Bearer $access_token" -d "{\"foo\": \"bar\"}"
```

## auth-get-sso-token

**This is a legacy tool and it will be removed in the future. It is NOT compatible with accounts that have "always-on 2FA". Please use one of the following available alternatives:**

- When getting access tokens for a user (interactive workflows): `auth-get-user-token`.
- For automated workflows: OAuth2 Client Credentials Grant or the [API-Access endpoint](https://auth.docs.cern.ch/user-documentation/oidc/api-access/).


This tool gets a user token for a public client using Kerberos credentials. The obtained token will be valid for 20 minutes.

```
$ auth-get-sso-token --help
usage: auth-get-sso-token [-h] [--url URL] [--clientid CLIENTID] [--nocertverify] [--verbose] [--debug] [--auth-server AUTH_SERVER] [--auth-realm AUTH_REALM]

Acquires a user token using implicit grant and Kerberos credentials

options:
  -h, --help            show this help message and exit
  --url URL, -u URL     Application or Redirect URL. Required for the OAuth request.
  --clientid CLIENTID, -c CLIENTID
                        Client ID of a client with implicit flow enabled
  --nocertverify        Disables peer certificate verification. Useful for debugging/tests when peer host does have a self-signed certificate for example.
  --verbose, -v         Provide more information on authentication process
  --debug, -vv          Provide detailed debugging information
  --auth-server AUTH_SERVER, -s AUTH_SERVER
                        Authentication server (default: auth.cern.ch)
  --auth-realm AUTH_REALM, -r AUTH_REALM
                        Authentication realm (default: cern)
```

Example:

```bash
TOKEN=$(./auth-get-sso-token -u http://localhost:5000 -c get-sso-token-test)
curl -X PUT "https://localhost:5000/api/foobar" -H  "authorization: Bearer $TOKEN" -d "{\"foo\": \"bar\"}"
```


## Limitations

Certificate credentials are not supported in the new SSO: you will get a warning message if you use the old options for certificates (`--cert`, `--key`, `--cacert`, `--capath`) or `--krb`. The behaviour of the tool will be exactly the same as if these options are not specified.


## Testing

Use unittest to test the `cern_sso` module. You will need a valid Kerberos TGT to run the tests.

```
python -m unittest test_cern_sso
```
