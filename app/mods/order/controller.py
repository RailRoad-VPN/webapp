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


def create_user_subscription(order_uuid: str, subscription_id: str) -> Optional[AjaxError]:
    logger.info('create_user_subscription method with parameters subscription_id: %s, order_uuid: %s' % (
        subscription_id, order_uuid))

    # create user subscription with created order
    logger.debug('get user_uuid and user_email')
    user_uuid = session['user']['uuid']
    user_email = session['user']['email']

    try:
        logging.info("Creating user subscription...")
        user_subscription = rrn_user_service.create_user_subscription(user_uuid=user_uuid,
                                                                      subscription_id=subscription_id,
                                                                      order_uuid=order_uuid)
        logging.info("User Subscription create: %s" % user_subscription)
    except APIException as e:
        logging.debug(e.serialize())
        error = AjaxError(message=DFNError.UNKNOWN_ERROR_CODE.message,
                          code=DFNError.UNKNOWN_ERROR_CODE.code,
                          developer_message=DFNError.UNKNOWN_ERROR_CODE.developer_message)
        return error

    logger.debug('send user email')
    email_service.send_new_sub_email(to_name=user_email, to_email=user_email)

    logger.debug('authorise user in system')
    authorize_user(user_json=session['user'])

    return None


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
        order_code_session = session['order']['order_code']
        logger.debug('order_code_session: %s' % order_code_session)

        if order_code_ppg == order_code_session:
            logger.error(
                "Order from PPG does not equal. Why? PPG: %s, Session: %s" % (order_code_ppg, order_code_session))

        subscription_id = session['order']['subscription_id']
        order_uuid = session['order']['order_uuid']

        error = create_user_subscription(order_uuid=order_uuid, subscription_id=subscription_id)
        return redirect(url_for('profile.profile_page', error=error))

    pack_id = request.args.get('pack', None)

    if 'order' not in session or session['order'] is None:
        # create new order
        try:
            logging.info("Creating order...")
            order_json = rrn_orders_service.create_order(status=OrderStatus.NEW)
            session['order'] = order_json
            logging.info("Order created: %s" % order_json)
        except APIException as e:
            logging.debug(e.serialize())

    subscriptions = subscription_service.get_subscriptions(lang_code=session['lang_code'])

    if subscriptions is None:
        return render_template('order/order.html', pack_id=pack_id, chosen_subscription=None,
                               subscriptions=None, code=200)

    logger.info("Got subscriptions. Size: %s" % len(subscriptions))
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


@mod_order.route('payment_url', methods=['GET'])
def payment_url():
    logger.info('generate_payment_redirect_url method')

    r = AjaxResponse(success=True)

    order_code = request.args.get('order_code', None)
    subscription_id = request.args.get('subscription_id', None)
    payment_method_id = request.args.get('payment_method_id', None)
    user_locale = session['user_locale']

    session['order']['subscription_id'] = subscription_id

    redirect_url = ppg_payments_service.build_redirect_url(order_code=order_code, subscription_id=subscription_id,
                                                           payment_method_id=payment_method_id, user_locale=user_locale)

    r.add_data('redirect_url', redirect_url)
    r.set_success()
    resp = jsonify(r.serialize())
    resp.code = HTTPStatus.OK
    return resp
