import logging

from flask import Blueprint, render_template

# Define the blueprint: 'index', set its url prefix: app.url/
mod_index = Blueprint('index', __name__, url_prefix='/')


@mod_index.route('/', methods=['GET', 'POST'])
def index():
    logging.info('index page')
    return render_template('index.html', code=200)
