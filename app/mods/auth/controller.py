import datetime
import json
import logging
import sys
from http import HTTPStatus

from flask import Blueprint, request, render_template, \
    g, session, redirect, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from app import rrn_usersapi_service, app_config, rrn_servicesapi_service, user_policy
from app.flask_utils import login_required, authorize_user, _add_language_code, _pull_lang_code
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError

sys.path.insert(0, '../rest_api_library')
from api import APIException, APINotFoundException
from utils import check_uuid

logger = logging.getLogger(__name__)

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/<lang_code>/auth')


@mod_auth.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_auth.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


@mod_auth.route('/signin', methods=['GET', 'POST'])
def signin():
    logger.info('signin method')

    if 'user' in session:
        return redirect(location=url_for("profile.profile_page"), code=201)

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
                user_json = rrn_usersapi_service.get_user(email=email)
            except APINotFoundException as e:
                logging.debug(e.serialize())
                r.set_failed()
                error = AjaxError(message=DFNError.USER_LOGIN_NOT_EXIST.message,
                                  code=DFNError.USER_LOGIN_NOT_EXIST.code,
                                  developer_message=DFNError.USER_LOGIN_NOT_EXIST.developer_message)
                r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = e.http_code
                return resp
            except APIException as e:
                logging.debug(e.serialize())
                r.set_failed()
                error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message, code=DFNError.UNKNOWN_ERROR_CODE.code,
                                  developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
                r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = e.http_code
                return resp

            is_password_valid = check_password_hash(user_json.get('password'), password)
            if not is_password_valid:
                r.set_failed()
                error = AjaxError(message=DFNError.USER_LOGIN_BAD_PASSWORD.message,
                                  code=DFNError.USER_LOGIN_BAD_PASSWORD.code,
                                  developer_message=DFNError.USER_LOGIN_BAD_PASSWORD.developer_message)
                r.add_error(error)
            elif not user_json.get('enabled'):
                r.set_failed()
                error = AjaxError(message=DFNError.USER_LOGIN_NOT_ENABLED.message,
                                  code=DFNError.USER_LOGIN_NOT_ENABLED.code,
                                  developer_message=DFNError.USER_LOGIN_NOT_ENABLED.developer_message)
                r.add_error(error)
            elif user_json.get('is_locked'):
                r.set_failed()
                error = AjaxError(message=DFNError.USER_LOGIN_LOCKED.message,
                                  code=DFNError.USER_LOGIN_LOCKED.code,
                                  developer_message=DFNError.USER_LOGIN_LOCKED.developer_message)
                r.add_error(error)
            elif user_json.get('is_expired'):
                r.set_failed()
                error = AjaxError(message=DFNError.USER_LOGIN_EXPIRED.message,
                                  code=DFNError.USER_LOGIN_EXPIRED.code,
                                  developer_message=DFNError.USER_LOGIN_EXPIRED.developer_message)
                r.add_error(error)
            else:
                authorize_user(user_json=user_json)
                r.set_success()
                r.set_next(url_for('profile.profile_page'))
                r.add_data("email", user_json['email'])
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
    else:
        return render_template('auth/signin.html', code=200)


@mod_auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logger.info('logout method')
    lang_code = session.get('lang_code')
    session.clear()
    # setup base data
    session['logged_in'] = False
    session['lang_code'] = lang_code
    session['locale'] = request.accept_languages.best
    g.user = None
    next = request.args.get('next', None)
    if next is not None:
        return redirect(next)
    return redirect(url_for('index.index_lang_page'))


@mod_auth.route('/isEmailBusy', methods=['GET'])
def is_email_busy():
    logger.info('is_email_busy method')

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
        rrn_usersapi_service.get_user(email=email)
        r.set_failed()
        error = AjaxError(message=DFNError.USER_SIGNUP_EMAIL_BUSY.message,
                          code=DFNError.USER_SIGNUP_EMAIL_BUSY.code,
                          developer_message=DFNError.USER_SIGNUP_EMAIL_BUSY.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
    except (APIException, APINotFoundException) as e:
        r.set_success()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp


@mod_auth.route('/update/email', methods=['POST'])
@login_required
def update_email():
    logger.info("update_email method")

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    email = data.get('email')

    try:
        # try to find user by email
        rrn_usersapi_service.get_user(email=email)
        r.set_failed()
        error = AjaxError(message=DFNError.USER_PROFILE_EMAIL_BUSY.message,
                          code=DFNError.USER_PROFILE_EMAIL_BUSY.code,
                          developer_message=DFNError.USER_PROFILE_EMAIL_BUSY.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp
    except APIException as e:
        user_json = session.get('user')
        user_json['email'] = email
        user_json['modify_reason'] = 'change email'

        rrn_usersapi_service.update_user(user_json=user_json)

        session['user'] = user_json

        r.set_success()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp


@mod_auth.route('/update/password', methods=['POST'])
@login_required
def update_password():
    logger.info("update_password method")

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    password = data.get('password')
    password = generate_password_hash(password)

    user_json = session['user']
    user_json['password'] = password
    user_json['modify_reason'] = 'change password'

    rrn_usersapi_service.update_user(user_json=user_json)

    session['user'] = user_json

    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_auth.route('/delete', methods=['POST'])
@login_required
def delete_account():
    logger.info("delete_account method")

    r = AjaxResponse(success=True)

    data = json.loads(request.data)

    email = data.get('email')

    user_json = session['user']

    if email != user_json['email']:
        r.set_failed()
        error = AjaxError(message=DFNError.USER_PROFILE_BAD_EMAIL_DELETE_ACCOUNT.message,
                          code=DFNError.USER_PROFILE_BAD_EMAIL_DELETE_ACCOUNT.code,
                          developer_message=DFNError.USER_PROFILE_BAD_EMAIL_DELETE_ACCOUNT.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    user_json['enabled'] = False
    user_json['modify_reason'] = 'delete account'

    rrn_usersapi_service.update_user(user_json=user_json)

    session['user'] = user_json

    r.set_success()
    r.set_next(url_for('auth.logout', lang_code=session['lang_code']))
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_auth.route('/is_trial_available', methods=['GET'])
def is_trial_available():
    logger.info("is_trial_available_url method")

    r = AjaxResponse(success=True)

    data = {
        'is_vpn_trial': True,
    }

    service_id = session.get('order').get('service_id', None)
    if service_id is None:
        r.set_failed()
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.BAD_REQUEST
        return resp

    if 'user' in session:
        user_uuid = session.get('user').get('uuid')
        data['is_vpn_trial'] = user_policy.is_trial_available_for_service(user_uuid=user_uuid, service_id=service_id)

    r.set_data(data)
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp
