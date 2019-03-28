import logging
import sys

from flask import Blueprint, render_template

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config
from app.flask_utils import _add_language_code, _pull_lang_code

sys.path.insert(0, '../rest_api_library')

mod_download = Blueprint('download', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_download.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_download.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_download.route('/download', methods=['GET'])
def download_page():
    logger.info('download_page method')
    return render_template('download/download.html', code=200)
