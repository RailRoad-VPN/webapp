import logging
import sys

from flask import Blueprint, render_template, session

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config
from app.flask_utils import _pull_lang_code, _add_language_code

sys.path.insert(0, '../rest_api_library')

mod_features = Blueprint('features', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_features.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_features.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_features.route('/features', methods=['GET'])
def features_page():
    logger.info('features_page method')
    return render_template('features/features.html', code=200)
