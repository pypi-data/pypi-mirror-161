"""Notelist package.

Notelist is a tag based note taking REST API that can be used to manage
notebooks, tags and notes. Notelist is based on the Flask framework.
"""

import sys
from datetime import timedelta

from flask import Flask, request, render_template, abort
from flask.wrappers import Response

from notelist.config import SettingsManager
from notelist.auth import jwt
from notelist.views import register_blueprints
from notelist.errors import register_error_handlers


__version__ = "0.10.0"

# Settings
sm = SettingsManager()

sec_key = sm.get("NL_SECRET_KEY")         # Secret Key
acc_exp = sm.get("NL_ACCESS_TOKEN_EXP")   # Access token expiration in minutes
ref_exp = sm.get("NL_REFRESH_TOKEN_EXP")  # Refresh token expiration in minutes

if sec_key is None:
    sys.exit("Error: 'NL_SECRET_KEY' setting not set.")

# Application object
app = Flask(__name__)

app.secret_key = sec_key
app.config["JSON_SORT_KEYS"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=acc_exp)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=ref_exp)

# User authentication (JWT)
jwt.init_app(app)

# Blueprints (view groups) and errors
register_blueprints(app)
register_error_handlers(app)


@app.route("/", methods=["GET"])
def index() -> str:
    """Return the API documentation page.

    The documentation page is returned only if the "NL_ROOT_DOC" environment
    variable is set and its value is "1". Otherwise, a HTML 404 error (Not
    Found) response is returned.

    :return: Documentation page (HTML code).
    """
    if sm.get("NL_ROOT_DOC") != 1:
        return abort(404)

    return render_template(
        "index.html", version=__version__, host_url=request.host_url
    )


@app.after_request
def after_request(response: Response) -> Response:
    """Modify each request response before sending it.

     This function sets the "Access-Control-Allow-Origin",
    "Access-Control-Allow-Methods" and "Access-Control-Allow-Headers" headers
    in every response of the API before sending it. These headers are related
    to CORS (Cross-Origin Resource Sharing).

    ### CORS (Cross-Origin Resource Sharing):

    The value of the "Access-Control-Allow-Origin" response header determines
    which host is allow to make requests to the API from a front-end
    application (from JavaScript code).

    If this API is used through a front-end application and the API and the
    front-end application are in the same host, then it's not needed to set
    this header. If the API and the front-end are in different hosts, then the
    header must be set to the host of the front-end application (starting with
    "https://").

    The value "*" for the header allows a front-end from any host to make
    requests to the API but this is not recommended and is not supported by all
    browsers.

    In this API, the value of the header is set through the "NL_ALLOW_ORIG"
    environment variable.

    :param response: Original response.
    :return: Final response.
    """
    response.access_control_allow_origin = sm.get("NL_ALLOW_ORIG")
    response.access_control_allow_methods = ["GET", "POST", "PUT", "DELETE"]

    response.access_control_allow_headers = [
        "Accept", "Content-Type", "Authorization"
    ]

    return response
