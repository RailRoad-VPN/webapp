import logging
import sys

from flask import Blueprint, render_template, session, abort

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config, rrnservice_service, RRNServiceType
from app.flask_utils import _pull_lang_code, _add_language_code

sys.path.insert(0, '../rest_api_library')

mod_pricing = Blueprint('pricing', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_pricing.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_pricing.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_pricing.route('/pricing', methods=['GET'])
def pricing_page():
    logger.info('pricing_page method')

    services = rrnservice_service.get_services_by_type(service_type=RRNServiceType.VPN_SUBSCRIPTION)

    if services is None:
        raise abort(404)

    return render_template('pricing/pricing.html', code=200, subscriptions=services)
