import json
import logging
import sys
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, request, render_template, \
    session, jsonify, redirect, url_for, abort

from app import rrn_user_service, rrn_orders_service, app_config, rrnservice_service, email_service, RRNServiceType
from app.flask_utils import _add_language_code, _pull_lang_code, authorize_user, login_required
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError
from app.models.order_status import OrderStatus
from app.models.user_service_status import UserServiceStatus

sys.path.insert(0, '../rest_api_library')
from rest import APIException

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_order = Blueprint('order', __name__, url_prefix='/<lang_code>/order')

logger = logging.getLogger(__name__)


@mod_order.url_defaults
def add_language_code(endpoint, values):
    _add_language_code(endpoint=endpoint, values=values)


@mod_order.url_value_preprocessor
def pull_lang_code(endpoint, values):
    _pull_lang_code(endpoint=endpoint, values=values, app_config=app_config)


def create_user_subscription(order_uuid: str, status_id: int, subscription_id: str) -> bool:
    logger.info('create_user_subscription method with parameters subscription_id: %s, order_uuid: %s' % (
        subscription_id, order_uuid))

    # create user subscription with created order
    logger.debug('get user_uuid and user_email')
    user_uuid = session.get('user').get('uuid')
    user_email = session.get('user').get('email')

    try:
        logger.info("Creating user subscription...")
        user_subscription = rrn_user_service.create_user_subscription(user_uuid=user_uuid, status_id=status_id,
                                                                      subscription_id=subscription_id,
                                                                      order_uuid=order_uuid)
        logger.error(f"user subscription was created: {user_subscription}")
    except APIException as e:
        logger.debug(e.serialize())
        return False

    logger.debug('get subscription name')
    subscriptions_dict = rrnservice_service.get_services_dict(lang_code=session.get('lang_code'))
    sub = subscriptions_dict.get(int(subscription_id))

    logger.debug('send user email')
    email_service.send_new_sub_email(to_name=user_email, to_email=user_email, sub_name=sub.get('name'))

    logger.debug('authorise user in system')
    authorize_user(user_json=session.get('user'))

    return True


@mod_order.route('', methods=['GET'])
def order_page():
    logger.info('order_page method')

    if 'order' not in session or session.get('order', None) is None:
        # create new order
        try:
            logger.info("create order")
            order_json = rrn_orders_service.create_order(status=OrderStatus.NEW.sid)
            session['order'] = order_json
            logger.debug("order created: %s" % order_json)
        except APIException as e:
            logger.debug(e.serialize())
            abort(500)

    subscriptions = rrnservice_service.get_services_by_type(service_type=RRNServiceType.VPN_SUBSCRIPTION)
    logger.debug("got subscriptions. Size: %s" % len(subscriptions))

    return render_template('order/order.html', subscriptions=subscriptions, code=200)


@mod_order.route('/payment_url', methods=['GET'])
def payment_url():
    logger.info('payment_url method')

    r = AjaxResponse(success=True)

    order_code = request.args.get('order_code', None)
    subscription_id = request.args.get('subscription_id', None)
    payment_method_id = request.args.get('payment_method_id', None)
    user_locale = session['user_locale']

    redirect_url = build_payment_url(user_uuid=session.get('user').get('uuid'), subscription_id=subscription_id,
                                     order_code=order_code, payment_method_id=payment_method_id,
                                     user_locale=user_locale)
    r.add_data('redirect_url', redirect_url)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


def build_payment_url(user_uuid: UUID, subscription_id: str, order_code: int, payment_method_id: int,
                      subscription_uuid: UUID = None, user_locale: str = None):
    session['order']['subscription_id'] = subscription_id

    redirect_url = ""

    session['order']['redirect_url'] = redirect_url
    return redirect_url


@mod_order.route('/<int:order_code>/payment')
@login_required
def get_order_payment(order_code: int):
    logger.info('get_order_payment method')

    r = AjaxResponse(success=True)

    try:
        order_json = rrn_orders_service.get_order(code=order_code)
    except APIException as e:
        logger.debug(e.serialize())
        r.set_failed()
        error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                          code=DFNError.UNKNOWN_ERROR_CODE.code,
                          developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        r.add_error(error)
        resp = jsonify(r.serialize())
        resp.code = HTTPStatus.OK
        return resp

    is_order_success = order_json['status_id'] == OrderStatus.SUCCESS.sid

    order_r = {
        'is_success': order_json['status_id'] == OrderStatus.SUCCESS.sid,
        'code': order_code
    }

    if is_order_success:
        api_response = rrn_orders_service.get_order_payments(order_uuid=order_json['uuid'])
        order_r['payments'] = api_response.data

    r.add_data('order', order_r)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp
