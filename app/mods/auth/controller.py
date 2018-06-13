import logging
import logging
import sys
from http import HTTPStatus

from flask import Blueprint, request, render_template, \
    g, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash

from app import rrn_user_service
from app.flask_utils import login_required, authorize_user
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from response import APIResponseStatus

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/<lang_code>/auth')


@mod_auth.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session['lang_code'])


@mod_auth.url_value_preprocessor
def pull_lang_code(endpoint, values):
    try:
        values.pop('lang_code')
    except:
        pass


@mod_auth.route('/signin', methods=['GET', 'POST'])
def signin():
    logging.info('signin method')
    r = AjaxResponse(success=True)
    if request.method == 'POST':
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        if email is None or email == '':
            r.set_failed()
            error = AjaxError(message=DFNError.USER_LOGIN_NOT_EXIST.message,
                              code=DFNError.USER_LOGIN_NOT_EXIST.code,
                              developer_message=DFNError.USER_LOGIN_NOT_EXIST.developer_message)
            r.add_error(error)
        elif password is None or password == '':
            r.set_failed()
            error = AjaxError(message=DFNError.USER_LOGIN_BAD_PASSWORD.message,
                              code=DFNError.USER_LOGIN_BAD_PASSWORD.code,
                              developer_message=DFNError.USER_LOGIN_BAD_PASSWORD.developer_message)
            r.add_error(error)
        else:
            try:
                api_response = rrn_user_service.get_user(email=email)
                if api_response.status == APIResponseStatus.success.status:
                    user_json = api_response.data
                else:
                    r.set_failed()
                    if api_response.errors is not None:
                        for err in api_response.errors:
                            error = AjaxError(message=err.message, code=err.code,
                                              developer_message=err['developer_message'])
                            r.add_error(error)
                    else:
                        error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                                          code=DFNError.UNKNOWN_ERROR_CODE.code,
                                          developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
                        r.add_error(error)
                    resp = jsonify(r.serialize())
                    resp.code = api_response.code
                    return resp
            except APIException as e:
                r.set_failed()
                # TODO fix it
                error = AjaxError(message='api not available', code='0', developer_message='something goes wrong')
                r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = e.http_code
                return resp
            is_ok = check_password_hash(user_json['password'], password)
            if not is_ok:
                r.set_failed()
                error = AjaxError(message=DFNError.USER_LOGIN_BAD_PASSWORD.message,
                                  code=DFNError.USER_LOGIN_BAD_PASSWORD.code,
                                  developer_message=DFNError.USER_LOGIN_BAD_PASSWORD.developer_message)
                r.add_error(error)
            else:
                authorize_user(user_json=user_json)
                r.set_success()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
    else:
        return render_template('auth/signin.html', code=200)


@mod_auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logging.info('logout method')
    lang_code = session['lang_code']
    session.clear()
    session['lang_code'] = lang_code
    g.user = None
    return redirect(url_for('index.index_lang_page'))


@mod_auth.route('/isEmailBusy', methods=['GET'])
def is_email_busy():
    logging.info('is_email_busy method')

    r = AjaxResponse(success=True)

    email = request.args.get('email', None)

    if email is None:
        r.set_failed()
        error = AjaxError(message=DFNError.USER_SIGNUP_EMAIL_BUSY.message,
                          code=DFNError.USER_SIGNUP_EMAIL_BUSY.code,
                          developer_message=DFNError.USER_SIGNUP_EMAIL_BUSY.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    try:
        # try to find user by email
        api_response = rrn_user_service.get_user(email=email)
        if api_response.status == APIResponseStatus.success.status:
            r.set_failed()
            error = AjaxError(message=DFNError.USER_SIGNUP_EMAIL_BUSY.message,
                              code=DFNError.USER_SIGNUP_EMAIL_BUSY.code,
                              developer_message=DFNError.USER_SIGNUP_EMAIL_BUSY.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.OK
            return resp

        r.set_success()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
    except APIException as e:
        logging.error("APIException", e)
        r.set_failed()
        error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                          code=DFNError.UNKNOWN_ERROR_CODE.code,
                          developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
