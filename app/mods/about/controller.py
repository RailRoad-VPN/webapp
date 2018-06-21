import logging
import sys

from flask import Blueprint, render_template

from app import app_config
from app.flask_utils import _add_language_code, _pull_lang_code

sys.path.insert(0, '../rest_api_library')

mod_about = Blueprint('about', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_about.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_about.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_about.route('/about', methods=['GET'])
def about_page():
    logger.info('about_page method')
    return render_template('about/about.html', code=200)
