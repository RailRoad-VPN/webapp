import logging
import sys
from http import HTTPStatus

from flask import Blueprint, request, render_template, \
    session, jsonify, abort

from app import rrn_billing_service, rrn_user_service, cache_service, rrn_orders_service
from app.flask_utils import authorize_user
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError
from order_status import OrderStatus

sys.path.insert(0, '../rest_api_library')
from rest import APIException, APINotFoundException

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_order = Blueprint('order', __name__, url_prefix='/<lang_code>/order')

logger = logging.getLogger(__name__)

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
    logger.info('order method')

    if request.method == 'POST':
        r = AjaxResponse(success=True)

        pack_id = request.form.get('pack_id', None)
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        password_repeat = request.form.get('password_repeat', None)

        if pack_id is None or email is None or password is None or password_repeat is None:
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
            rrn_user_service.get_user(email=email)
            r.set_failed()
            error = AjaxError(message=DFNError.USER_SIGNUP_EMAIL_BUSY.message,
                              code=DFNError.USER_SIGNUP_EMAIL_BUSY.code,
                              developer_message=DFNError.USER_SIGNUP_EMAIL_BUSY.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.OK
            return resp
        except APINotFoundException as e:
            pass
        except APIException as e:
            logging.debug(e.serialize())
            r.set_failed()
            error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                              code=DFNError.UNKNOWN_ERROR_CODE.code,
                              developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = e.http_code
            return resp

        try:
            # try to register user
            try:
                user_json = rrn_user_service.create_user(email=email, password=password)
                user_json.pop('password')
                logging.info("Registered user: %s" % user_json)
            except APIException as e:
                logger.debug(e.serialize())
                r.set_failed()
                error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                                  code=DFNError.UNKNOWN_ERROR_CODE.code,
                                  developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
                r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = e.http_code
                return resp
            authorize_user(user_json=user_json)
            logging.info("User authorized")

            # create order with status - new
            try:
                logging.info("Creating order...")
                order_json = rrn_orders_service.create_order(status=OrderStatus.NEW)
                logging.info("Order created: %s" % order_json)
            except APIException as e:
                logging.debug(e.serialize())
                r.set_failed()
                error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                                  code=DFNError.UNKNOWN_ERROR_CODE.code,
                                  developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
                r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = e.http_code
                return resp

            # create user subscription with created order
            user_uuid = user_json['uuid']
            order_uuid = order_json['uuid']

            try:
                logging.info("Creating user subscription...")
                user_subscription = rrn_user_service.create_user_subscription(user_uuid=user_uuid,
                                                                              subscription_id=pack_id,
                                                                              order_uuid=order_uuid)
                logging.info("User Subscription create: %s" % user_subscription)
            except APIException as e:
                logging.debug(e.serialize())
                r.set_failed()
                error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                                  code=DFNError.UNKNOWN_ERROR_CODE.code,
                                  developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
                r.add_error(error)
                resp = jsonify(r.serialize())
                resp.code = e.http_code
                return resp

            # TODO send email about account and order

            r.set_success()
            r.add_data('order', order_json)
            r.add_data('user', user_json)

            resp = jsonify(r.serialize())
            resp.code = HTTPStatus.OK
            return resp
        except APIException as e:
            logging.debug(e.serialize())
            r.set_failed()
            error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                              code=DFNError.UNKNOWN_ERROR_CODE.code,
                              developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
            r.add_error(error)
            resp = jsonify(r.serialize())
            resp.code = e.http_code
            return resp
    else:
        pack_id = request.args.get('pack', None)
        subscriptions = cache_service.get(key='subscriptions', prefix=session['lang_code'])
        if subscriptions is None:
            try:
                subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
                cache_service.set('subscriptions', subscriptions)
            except APIException as e:
                pass

        subscription = None
        if pack_id is not None:
            for sub in subscriptions:
                if str(sub['id']) == pack_id:
                    subscription = sub
                    break

        if pack_id is not None and subscription is None:
            # TODO think here
            raise abort(404)

        return render_template('index/order.html', pack_id=pack_id, chosen_subscription=subscription,
                               subscriptions=subscriptions, code=200)
