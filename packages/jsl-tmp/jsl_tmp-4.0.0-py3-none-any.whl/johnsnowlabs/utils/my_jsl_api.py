import json
from urllib.request import Request, urlopen
import os

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.request import Request, urlopen
import os

import argparse

# imports related to get access token with PKCE Oauth
from urllib import parse
import string
import base64
import random
import hashlib
import webbrowser
MYJSL_ORIGIN = os.environ.get("MYJSL_ORIGIN", "https://my.johnsnowlabs.com")

# save_path that license should be downloaded there
LICENSE_PATH = "downloaded-license.json"


# using urllib to avoid additional package dependencies like requests

def http_request(url, data=None, method="POST", is_json=True, ACCESS_TOKEN=None):
    if data:
        if is_json:
            data = json.dumps(data).encode("utf-8")
        else:
            data = parse.urlencode(data).encode("utf-8")
    request = Request(url, data=data, method=method)
    if ACCESS_TOKEN:
        request.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    if is_json:
        request.add_header("Content-Type", "application/json")
    else:
        request.add_header("Content-type", "application/x-www-form-urlencoded")
    response = urlopen(request)
    status_code = response.getcode()
    return (
        json.loads(response.read().decode("utf-8"))
        if 200 <= status_code < 300
        else None
    )


def get_access_token(email, password):
    """get access token (expires in 12h)"""
    data = http_request(
        MYJSL_ORIGIN + "/graphql",
        data={
            "query": """mutation($input: LoginInput!) {
                getAccessToken(input: $input) {
                    ok {token}
                    error {
                        errors {
                          key
                          message
                        }
                    }
                }
            }""",
            "variables": {"input": {"email": email, "password": password}},
        },
    )
    if data["data"]["getAccessToken"]["error"]:
        errors = "\n".join(
            [
                error["message"]
                for error in data["data"]["getAccessToken"]["error"]["errors"]
            ]
        )
        print(f"Cannot login. error={errors}")
        exit(1)
    access_token = data["data"]["getAccessToken"]["ok"]["token"]
    return access_token


def get_user_licenses(ACCESS_TOKEN):
    licenses_query = """query LicensesQuery {
  licenses(isValid: true, platforms: ["Airgap", "Floating"]) {
    edges {
      node {
        id
        type
        endDate
        platform {
          file_name
          type
        }
        products {
          file_name
        }
      }
    }
  }
}
 """
    data = http_request(f"{MYJSL_ORIGIN}/graphql", {"query": licenses_query}, ACCESS_TOKEN=ACCESS_TOKEN)
    if data:
        if "errors" in data:
            raise Exception("Invalid or Expired token.")
        licenses = [s["node"] for s in data["data"]["licenses"]["edges"]]
    else:
        raise Exception("Something went wrong...")
    return licenses


def download_license(license, ACCESS_TOKEN):
    print("Downloading license...")
    data = http_request(
        "{}/attachments/{}".format(MYJSL_ORIGIN, license["id"]), method="GET",
        ACCESS_TOKEN=ACCESS_TOKEN
    )
    if data:
        # print("Licenses extracted successfully")
        return data
    else:
        raise Exception(f"Failed fetching license.")





def ensure_correct_choice(licenses_count):
    license_id = input()
    if license_id.isnumeric():
        index = int(license_id) - 1
        if licenses_count > index:
            return index
        else:
            print(f"Please select value between 1 and {licenses_count}")
            return ensure_correct_choice(licenses_count)
    else:
        print(f"Please select value between 1 and {licenses_count}")
        return ensure_correct_choice(licenses_count)


def get_user_license_choice(licenses):
    print("Please select the license to use.")
    for idx, license in enumerate(licenses):
        products = ",".join(s["file_name"] for s in license["products"])
        if license["platform"] is None:
            scope = "Airgap"
        else:
            scope = license["platform"]["file_name"]
            type = license["platform"]["type"]
            if scope == "Floating":
                if type:
                    scope = scope + "," + type.capitalize()

        print(
            "{}. Libraries: {}\n   License Type: {}\n   Expiration Date: {}\n   Scope: {}".format(
                idx + 1, products, license["type"], license["endDate"], scope
            )
        )

    choice = ensure_correct_choice(len(licenses))
    return licenses[choice]

def get_access_key_from_browser():
    client_id = "sI4MKSmLHOX2Pg7XhM3McJS2oyKG5PHcp0BlANEW"

    class OauthRequestHandler(BaseHTTPRequestHandler):
        code = None

        def response(self, msg, code):
            self.send_response(code)
            self.end_headers()
            self.wfile.write(
                f"<html><head><title>Johnsnowlabs</title><head><body>"
                f"<div style='text-align:center;margin-top:100px;'>"
                f"<span style='color:{'#0298d9' if code == 200 else '#c0392b'};font-size:24px'>{msg}</span>"
                f"</div></body></html>".encode("utf-8")
            )

        def do_GET(self):
            global access_token
            url_parts = parse.urlsplit(self.path)
            if url_parts.path == "/login":
                params = dict(parse.parse_qsl(url_parts.query))
                OauthRequestHandler.code = params.get("code")
                if OauthRequestHandler.code:
                    self.response("Authorization successful!", 200)
                else:
                    self.response("Authorization failed! please try again.", 400)

    verifier = "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(64)]
    )
    hashed = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(hashed)[:-1].decode("utf-8")

    with HTTPServer(("", 0), OauthRequestHandler) as httpd:
        port = httpd.server_port
        url = "{}/oauth/authorize/?{}".format(
            MYJSL_ORIGIN,
            parse.urlencode(
                {
                    "client_id": client_id,
                    "response_type": "code",
                    "code_challenge_method": "S256",
                    "code_challenge": challenge,
                    "redirect_uri": f"http://localhost:{port}/login",
                }
            ),
        )
        print("Please confirm authorization on :", url)
        webbrowser.open_new_tab(url)
        httpd.handle_request()

    if OauthRequestHandler.code:
        data = http_request(
            f"{MYJSL_ORIGIN}/oauth/token/",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "code_verifier": verifier,
                "code": OauthRequestHandler.code,
                "redirect_uri": f"http://localhost:{port}/login",
            },
            is_json=False,
        )
        return data["access_token"]
    return None


# if __name__ == "__main__":
#         # get token from acces
#         # ACCESS_TOKEN = get_access_token(args.email, password)
#         # get available licenses
#         licenses = get_user_licenses(ACCESS_TOKEN)
#         # if more than once license, show options
#     if len(licenses) == 0:
#         raise Exception(
#             f"It seems there are no compatible licenses available. Please request a license first using {MYJSL_ORIGIN}"
#         )
#     if len(licenses) == 1:
#         license_to_use = licenses[0]
#     else:
#         license_to_use = get_user_license_choice(licenses)
#     # download license to file
#     download_license(license_to_use)
# except Exception as e:
#     print(e)
#     exit(1)


# registerListenerAndStartRefresh auto-referesh credentials