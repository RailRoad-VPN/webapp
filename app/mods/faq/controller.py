import logging
import sys

from flask import Blueprint, render_template, session

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config
from app.flask_utils import _add_language_code, _pull_lang_code

sys.path.insert(0, '../rest_api_library')

mod_faq = Blueprint('faq', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_faq.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_faq.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_faq.route('/faq', methods=['GET'])
def faq_page():
    logger.info('faq_page method')
    return render_template('faq/faq.html', code=200)
