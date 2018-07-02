import datetime
import logging
import sys
import uuid
from http import HTTPStatus

from flask import Blueprint, render_template, request, jsonify

# Define the blueprint: 'index', set its url prefix: app.url/
from app import app_config
from app.flask_utils import _add_language_code, _pull_lang_code
from app.models import AjaxResponse

sys.path.insert(0, '../rest_api_library')

mod_contact = Blueprint('contact', __name__, url_prefix='/<lang_code>/')

logger = logging.getLogger(__name__)


@mod_contact.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_contact.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_contact.route('/contact', methods=['GET', 'POST'])
def contact():
    logger.info('contact method')

    if request.method == 'POST':
        r = AjaxResponse(success=True)

        name = request.form.get('name', None)
        email = request.form.get('email', None)
        message = request.form.get('message', None)

        data = "name=%s,email=%s,message=%s" % (name, email, message)

        # TODO send email

        t = '{0:%Y_%m_%d_%H%M%S}'.format(datetime.datetime.now())
        tt = "%s_%s" % (t, uuid.uuid4())

        with open('%s/%s.data' % (app_config['FS']['contact'], tt), 'w') as file:
            file.write(data)
            file.close()

        r.set_success()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
    else:
        return render_template('contact/contact.html', code=200)
