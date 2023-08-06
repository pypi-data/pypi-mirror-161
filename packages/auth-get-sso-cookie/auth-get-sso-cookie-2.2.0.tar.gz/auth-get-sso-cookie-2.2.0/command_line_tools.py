#!/usr/bin/env python
from datetime import datetime, timedelta
from auth_get_sso_cookie import cern_sso

import os
import logging
import argparse
import urllib3
import sys
import json

AUTH_HOSTNAME = "auth.cern.ch"
AUTH_REALM = "cern"


def _add_common_arguments(parser):
    parser.add_argument(
        "--nocertverify",
        action="store_true",
        help="Disables peer certificate verification. Useful for debugging/tests when peer host does have a self-signed certificate for example.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Provide more information on authentication process",
    )
    parser.add_argument(
        "--debug",
        "-vv",
        action="store_true",
        help="Provide detailed debugging information",
    )
    parser.add_argument(
        "--auth-server",
        "-s",
        default="auth.cern.ch",
        help="Authentication server (default: auth.cern.ch)",
    )


def _configure_logging(args):
    log_level = logging.WARNING
    if args.verbose:
        log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")


def _show_https_cert_warning(args):
    if args.nocertverify:
        logging.warning(
            "Certificate verification is turned off. If you are not running this for test purposes, remove the --nocertverify option."
        )
        urllib3.disable_warnings()


def auth_get_sso_cookie():
    parser = argparse.ArgumentParser(
        description="Acquires the CERN Single Sign-On cookie using Kerberos credentials"
    )
    parser.add_argument(
        "-u", "--url", type=str, help="CERN SSO protected site URL to get cookie for."
    )
    parser.add_argument(
        "-o", "--outfile", type=str, help="File to store the cookie for further usage"
    )
    parser.add_argument("--krb", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--cert", help=argparse.SUPPRESS)
    parser.add_argument("--key", help=argparse.SUPPRESS)
    parser.add_argument("--cacert", help=argparse.SUPPRESS)
    parser.add_argument("--reprocess", help=argparse.SUPPRESS)
    _add_common_arguments(parser)
    args = parser.parse_args()

    _configure_logging(args)

    if not args.url:
        logging.error(
            "-u https://.... option is mandatory, see auth-get-sso-cookie.py --help for help."
        )
        raise TypeError(
            "-u https://.... option is mandatory, see auth-get-sso-cookie.py --help for help.")
    if not args.outfile:
        logging.error(
            "-o cookiefile.txt option is mandatory, see auth-cern-sso-cookie.py --help for help."
        )
        raise TypeError(
            "-o cookiefile.txt option is mandatory, see auth-cern-sso-cookie.py --help for help.")
    if args.krb or args.cert or args.key or args.cacert:
        logging.warning(
            "You are using an obsolete option. Certificate credentials are no longer supported: this utility only uses Kerberos."
        )
    _show_https_cert_warning(args)

    try:
        # First check if cookie already exists
        if os.path.isfile(args.outfile):
            with open(args.outfile, 'r') as file:
                try:
                    keycloak_sessions = [line.split(
                        '\t') for line in file.readlines() if "KEYCLOAK_SESSION" in line]
                    # Ensure cookie has at least 10 minutes of validity left.
                    current_ts = datetime.now() - timedelta(minutes=10)
                    # Netscape format always adds timestamp as the 5th index: https://unix.stackexchange.com/a/210282/359160
                    expire_ts = datetime.utcfromtimestamp(
                        int(keycloak_sessions[0][4]))
                    if expire_ts > current_ts:
                        logging.warning("The existing cookie in file '{}' is still valid until {}. This run will not start a new session, please use the existing file.".format(
                            args.outfile, expire_ts))
                        return
                except:
                    # If the cookie file is malformed, continue with getting a new cookie.
                    pass
        cern_sso.save_sso_cookie(
            args.url, args.outfile, not args.nocertverify, args.auth_server)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


def auth_get_sso_token():
    parser = argparse.ArgumentParser(
        description="Acquires a user token using implicit grant and Kerberos credentials"
    )
    parser.add_argument(
        "--url",
        "-u",
        type=str,
        help="Application or Redirect URL. Required for the OAuth request.",
    )
    parser.add_argument(
        "--clientid",
        "-c",
        type=str,
        help="Client ID of a client with implicit flow enabled",
    )
    _add_common_arguments(parser)
    parser.add_argument(
        "--auth-realm",
        "-r",
        default="cern",
        help="Authentication realm (default: cern)",
    )
    args = parser.parse_args()

    _configure_logging(args)

    if not args.url:
        logging.error(
            "-u http(s)://.... option is mandatory, see auth-get-sso-token.py --help for help."
        )
        raise TypeError(
            "-u http(s)://.... option is mandatory, see auth-get-sso-token.py --help for help.")

    if not args.clientid:
        logging.error(
            "-c <client-id> option is mandatory, see auth-get-sso-token.py --help for help."
        )
        raise TypeError(
            "-c <client-id> option is mandatory, see auth-get-sso-token.py --help for help.")

    _show_https_cert_warning(args)

    try:
        token = cern_sso.get_sso_token(
            args.url, args.clientid, not args.nocertverify, args.auth_server, args.auth_realm)
        print(token)
    except Exception as e:
        logging.error(e)
        sys.exit(1)


def auth_get_user_token():
    parser = argparse.ArgumentParser(
        description="Acquires a user token using device authorization grant. It does not require any local credentials."
    )
    parser.add_argument(
        "--clientid",
        "-c",
        type=str,
        help="Client ID of a public client with device authorization grant enabled",
    )
    parser.add_argument(
        "--auth-realm",
        "-r",
        default="cern",
        help="Authentication realm (default: cern)",
    )
    parser.add_argument(
        "--extract-token",
        "-x",
        action="store_true",
        help="Extract and save only the access token instead of the full response json",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=str,
        help="File to store the token for further usage"
    )
    parser.add_argument(
        "-a",
        "--audience",
        type=str,
        help="Exchange token for another target audience or client ID"
    )
    _add_common_arguments(parser)
    args = parser.parse_args()

    _configure_logging(args)

    if not args.clientid:
        logging.error(
            "-c <client-id> option is mandatory, see auth-get-user-token.py --help for help."
        )
        raise TypeError(
            "-c <client-id> option is mandatory, see auth-get-user-token.py --help for help.")
    if not args.outfile:
        logging.error(
            "-o token.txt option is mandatory, see auth-cern-user-token.py --help for help."
        )
        raise TypeError(
            "-o token.txt option is mandatory, see auth-cern-user-token.py --help for help.")

    _show_https_cert_warning(args)

    try:
        token = cern_sso.device_authorization_login(
            args.clientid, not args.nocertverify, args.auth_server, args.auth_realm)
        if args.audience:
            token = cern_sso.public_token_exchange(
                args.clientid, args.audience, token['access_token'], args.auth_server, args.auth_realm, not args.nocertverify)
        with open(args.outfile, 'w') as file:
            if args.extract_token:
                file.write(token['access_token'])
            else:
                file.write(json.dumps(token))
    except Exception as e:
        logging.error(e)
        sys.exit(1)
