import logging
import sys

from flask import Blueprint, render_template, request

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config
from app.flask_utils import _add_language_code, _pull_lang_code

sys.path.insert(0, '../rest_api_library')

mod_blog = Blueprint('blog', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_blog.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_blog.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_blog.route('/blog', methods=['GET', 'POST'])
def blog_page():
    logger.info('blog_page method')
    return render_template('blog/blog.html', code=200)


@mod_blog.route('/blog/<string:article_name>', methods=['GET'])
def article_page(article_name: str):
    logger.info('article_page method')
    return render_template('blog/articles/%s.html' % article_name, code=200)
