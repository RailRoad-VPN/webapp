import logging
import sys

from flask import Blueprint, render_template

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config
from app.flask_utils import _add_language_code, _pull_lang_code

sys.path.insert(0, '../rest_api_library')

mod_contact = Blueprint('contact', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_contact.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_contact.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_contact.route('/contact', methods=['GET'])
def contact_page():
    logger.info('contact_page method')
    return render_template('contact/contact.html', code=200)
