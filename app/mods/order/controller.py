import logging
import sys
from http import HTTPStatus
from typing import Optional

from flask import Blueprint, request, render_template, \
    session, jsonify, redirect, url_for

from app import rrn_user_service, rrn_orders_service, app_config, \
    ppg_payments_service, subscription_service, email_service
from app.flask_utils import _add_language_code, _pull_lang_code, authorize_user
from app.models import AjaxResponse, AjaxError
from app.models.exception import DFNError
from app.models.order_status import OrderStatus
from app.models.user_subscription_status import UserSubscriptionStatus

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
        logging.info("Creating user subscription...")
        user_subscription = rrn_user_service.create_user_subscription(user_uuid=user_uuid,
                                                                      status_id=status_id,
                                                                      subscription_id=subscription_id,
                                                                      order_uuid=order_uuid)
        logging.info("User Subscription create: %s" % user_subscription)
    except APIException as e:
        logging.debug(e.serialize())
        return False

    logger.debug('get subscription name')
    subscriptions_dict = subscription_service.get_subscriptions_dict(lang_code=session.get('lang_code'))
    sub = subscriptions_dict.get(int(subscription_id))

    logger.debug('send user email')
    email_service.send_new_sub_email(to_name=user_email, to_email=user_email, sub_name=sub.get('name'))

    logger.debug('authorise user in system')
    authorize_user(user_json=session['user'])

    return True


@mod_order.route('', methods=['GET', 'POST'])
def order():
    logger.info('order method')

    logger.debug('check x-ordercode in request arguments and order in session')
    if 'x-ordercode' in request.args and 'order' in session:
        logger.debug('we have x-ordercode in request arguments and order in session')
        logger.debug('get x-ordercode')
        order_code_ppg = request.args.get('x-ordercode', None)
        logger.debug('x-ordercode: %s' % order_code_ppg)

        logger.debug('get order code from order in session')
        order_code_session = session['order']['code']
        logger.debug('order_code_session: %s' % order_code_session)

        if order_code_ppg == order_code_session:
            logger.error(
                "Order from PPG does not equal. Why? PPG: %s, Session: %s" % (order_code_ppg, order_code_session))

        subscription_id = session['order']['subscription_id']
        order_uuid = session.get('order').get('uuid')

        is_ok = create_user_subscription(order_uuid=order_uuid, subscription_id=subscription_id,
                                         status_id=UserSubscriptionStatus.WAIT_FOR_PAYMENT.sid)
        if not is_ok:
            logger.error(f"user subscription was not created")
            logger.debug(f"set order {order_code_ppg} status failed")
            order_json = session.get('order')
            order_json['status_id'] = OrderStatus.FAILED.sid
        else:
            logger.error(f"user subscription was created")

            logger.debug(f"Set order {order_code_ppg} status processing")
            order_json = session.get('order')
            order_json['status_id'] = OrderStatus.PROCESSING.sid

        logger.debug("remove order from session")
        session.pop('order')

        order_json['modify_reason'] = 'update order status'
        rrn_orders_service.update_order(order_json=order_json)
        return redirect(url_for('profile.profile_page'))
    elif 'x-ordercode' not in request.args and 'order' in session and 'redirect_url' in session['order']:
        if 'error' in request.args:
            error = request.args.get('error', None)
            logger.error(f"PayProGlobal error: {error}")
            return redirect(session['order']['redirect_url'])

    pack_id = request.args.get('pack', None)

    if 'order' not in session or session['order'] is None:
        # create new order
        try:
            logging.info("creating order...")
            order_json = rrn_orders_service.create_order(status=OrderStatus.NEW.sid)
            session['order'] = order_json
            logging.info("order created: %s" % order_json)
        except APIException as e:
            logging.debug(e.serialize())

    subscriptions = subscription_service.get_subscriptions(lang_code=session.get('lang_code'))

    if subscriptions is None:
        return redirect(url_for('order/order', lang_code=session.get('lang_code')))

    logger.info("got subscriptions. Size: %s" % len(subscriptions))
    if app_config['DEBUG'] is True:
        for sub in subscriptions:
            logger.debug(sub)

    subscription = None
    if pack_id is not None:
        for sub in subscriptions:
            if str(sub['id']) == pack_id:
                subscription = sub
                break

    return render_template('order/order.html', pack_id=pack_id, chosen_subscription=subscription,
                           subscriptions=subscriptions, code=200)


@mod_order.route('/payment_url', methods=['GET'])
def payment_url():
    logger.info('payment_url method')

    r = AjaxResponse(success=True)

    order_code = request.args.get('order_code', None)
    subscription_id = request.args.get('subscription_id', None)
    payment_method_id = request.args.get('payment_method_id', None)
    user_locale = session['user_locale']

    session['order']['subscription_id'] = subscription_id

    redirect_url = ppg_payments_service.build_redirect_url(user_uuid=session.get('user').get('uuid'),
                                                           order_code=order_code, subscription_id=subscription_id,
                                                           payment_method_id=payment_method_id, user_locale=user_locale)

    session['order']['redirect_url'] = redirect_url

    # logger.debug(f"set order {session['order']['code']} status processing")
    # order_json = session['order']
    # order_json['modify_reason'] = 'update status'
    # order_json['status_id'] = OrderStatus.NEW.sid
    #
    # rrn_orders_service.update_order(order_json=order_json)

    r.add_data('redirect_url', redirect_url)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp


@mod_order.route('/<int:order_code>/payment')
def get_order_payment(order_code: int):
    logger.info('get_order_payment method')

    r = AjaxResponse(success=True)

    try:
        order_json = rrn_orders_service.get_order(code=order_code)
    except APIException as e:
        logging.debug(e.serialize())
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
