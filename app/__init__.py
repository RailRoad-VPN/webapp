import os
from pprint import pprint

from flask import Flask, url_for, redirect, session, request
from flask_babel import Babel
from flask_moment import Moment

from app.cache import CacheService
from app.service import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')

app = Flask(__name__)

babel = Babel(app)

# TODO i10n dates
moment = Moment(app)

from app import cli

# Load config based on env variable
ENVIRONMENT_CONFIG = os.environ.get("ENVIRONMENT_CONFIG", default='DevelopmentConfig')
logger.info("Got ENVIRONMENT_CONFIG variable: %s" % ENVIRONMENT_CONFIG)
config_name = "%s.%s" % ('config', ENVIRONMENT_CONFIG)
logger.info("Config name: %s" % config_name)
app.config.from_object(config_name)

app_config = app.config

cache_service = CacheService(app=app)

rrn_user_service = RRNUsersAPIService(api_url=app.config['API_URL'],
                                      resource_name=app.config['USERS_API_RESOURCE_NAME'])

rrn_billing_service = RRNBillingAPIService(api_url=app.config['API_URL'],
                                           resource_name=app.config['SUBSCRIPTIONS_API_RESOURCE_NAME'])

rrn_orders_service = RRNOrdersAPIService(api_url=app.config['API_URL'],
                                         resource_name=app.config['ORDERS_API_RESOURCE_NAME'])

ppg_payments_service = PayProGlobalPaymentService(config=app_config)

from app.flask_utils import before_request, get_locale

app.before_request(before_request)

from app.mods.auth.controller import mod_auth as auth_module

app.register_blueprint(auth_module)

from app.mods.index.controller import mod_index as index_module

app.register_blueprint(index_module)

from app.mods.profile.controller import mod_profile as profile_module

app.register_blueprint(profile_module)

from app.mods.order.controller import mod_order as order_module

app.register_blueprint(order_module)


@app.route('/', methods=['GET'])
def index_page():
    logger.info('index page')
    redirect_url = url_for('index.index_lang_page', lang_code=session['lang_code'])
    return redirect(redirect_url)


pprint(app.url_map._rules_by_endpoint)
