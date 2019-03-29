import logging
import sys

from flask import Blueprint, render_template

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config, user_policy
from app.flask_utils import _pull_lang_code, _add_language_code

sys.path.insert(0, '../rest_api_library')
from api import APIException

mod_index = Blueprint('index', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_index.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_index.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_index.route('/', methods=['GET'])
def index_lang_page():
    logger.info('index_lang page')

    try:
        vpn_subs_services = user_policy.get_user_available_services()
    except APIException:
        vpn_subs_services = None

    return render_template('index/index.html', code=200, vpn_subs_services=vpn_subs_services)


@mod_index.route('/privacy-policy', methods=['GET'])
def privacy_policy_page():
    logger.info('privacy_policy_page page')

    return render_template('index/privacy-policy.html', code=200)


@mod_index.route('/terms-of-service', methods=['GET'])
def terms_of_service_page():
    logger.info('terms_of_service_page page')

    return render_template('index/terms-of-service.html', code=200)
