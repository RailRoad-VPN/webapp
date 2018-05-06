from pprint import pprint

import logging
from flask import Flask
from flask_babel import Babel
from flask_moment import Moment

from app.service import UserService

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

babel = Babel(app)

# TODO i10n dates
moment = Moment(app)

from app import cli

# Load the default configuration
app.config.from_object('config.DevelopmentConfig')

user_service = UserService(api_url=app.config['USER_SERVICE_URL'])

from app.flask_utils import before_request

app.before_request(before_request)

from app.mods.auth.controller import mod_auth as auth_module

app.register_blueprint(auth_module)

from app.mods.index.controller import mod_index as index_module

app.register_blueprint(index_module)

from app.mods.profile.controller import mod_profile as profile_module

app.register_blueprint(profile_module)

pprint(app.url_map._rules_by_endpoint)
