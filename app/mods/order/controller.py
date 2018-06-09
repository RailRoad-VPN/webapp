import logging
import logging
import sys
from http import HTTPStatus

from flask import Blueprint, request, render_template, \
    session, jsonify

from app import rrn_billing_service, rrn_user_service
from app.models import AjaxResponse, AjaxError
from auth.controller import authorize_user
from app.models.exception import DFNError

sys.path.insert(0, '../rest_api_library')
from rest import APIException

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_order = Blueprint('order', __name__, url_prefix='/<lang_code>/order')


@mod_order.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session['lang_code'])


@mod_order.url_value_preprocessor
def pull_lang_code(endpoint, values):
    try:
        values.pop('lang_code')
    except:
        pass


@mod_order.route('', methods=['GET', 'POST'])
def order():
    logging.info('order method')

    pack = request.args.get('pack', None)

    if request.method == 'POST':
        r = AjaxResponse(success=True)

        email = request.args.get('email', None)
        password = request.args.get('password', None)
        password_repeat = request.args.get('password_repeat', None)

        if pack is None or email is None or password is None or password_repeat is None:
            r.set_failed()
            error = AjaxError(message=DFNError.ORDER_SUB_FIELDS_INCOMPLETE.message,
                              code=DFNError.ORDER_SUB_FIELDS_INCOMPLETE.code,
                              developer_message=DFNError.ORDER_SUB_FIELDS_INCOMPLETE.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.OK
            return resp
        elif password != password_repeat:
            r.set_failed()
            error = AjaxError(message=DFNError.ORDER_SUB_FIELDS_INCOMPLETE.message,
                              code=DFNError.ORDER_SUB_FIELDS_INCOMPLETE.code,
                              developer_message=DFNError.ORDER_SUB_FIELDS_INCOMPLETE.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.OK
            return resp

        try:
            # try to find user by email
            user_by_email = rrn_user_service.get_user(email=email)
            if user_by_email is not None:
                error = AjaxError(message=DFNError.USER_SIGNUP_EMAIL_BUSY.message,
                                  code=DFNError.USER_SIGNUP_EMAIL_BUSY.code,
                                  developer_message=DFNError.USER_SIGNUP_EMAIL_BUSY.developer_message)
                r.add_error(error)
                resp = jsonify(r)
                resp.code = HTTPStatus.OK
                return resp
        except APIException as e:
            error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                              code=DFNError.UNKNOWN_ERROR_CODE.code,
                              developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
            r.add_error(error)
            resp = jsonify(r)
            resp.code = e.http_code
            return resp

        try:
            # try to register user
            user_json = {
                'email': email,
                'password': password,
                'password_repeat': password_repeat,
            }
            api_response = rrn_user_service.create_user(user_json=user_json)

            if not api_response.is_ok and api_response.errors is not None:
                for err in api_response.errors:
                    error = AjaxError(message=err.code, code=err.message, developer_message=err.developer_message)
                    r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = HTTPStatus.OK
                return resp

            user_json = api_response.data
            authorize_user(user_json=user_json)

            # TODO create subscription request

            r.set_success()

            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.OK
            return resp
        except APIException as e:
            error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                              code=DFNError.UNKNOWN_ERROR_CODE.code,
                              developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
            r.add_error(error)
            resp = jsonify(r)
            resp.code = e.http_code
            return resp

    else:
        subscriptions = None
        try:
            subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
        except APIException as e:
            pass

        return render_template('index/order.html', pack=pack, subscriptions=subscriptions, code=200)
