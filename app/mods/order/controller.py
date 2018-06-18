import logging
import sys
from http import HTTPStatus

from flask import Blueprint, request, render_template, \
    session, jsonify, abort

from app import rrn_billing_service, rrn_user_service, cache_service, rrn_orders_service, app_config
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
    values.setdefault('lang_code', session['lang_code'])


@mod_order.url_value_preprocessor
def pull_lang_code(endpoint, values):
    try:
        values.pop('lang_code')
    except:
        pass


def create_user_subscription():
    logger.info('create_user_subscription method')

    r = AjaxResponse(success=True)

    # create user subscription with created order
    user_uuid = session['user']['uuid']
    subscription_id = ''
    order_uuid = ''

    try:
        logging.info("Creating user subscription...")
        user_subscription = rrn_user_service.create_user_subscription(user_uuid=user_uuid,
                                                                      subscription_id=subscription_id,
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


@mod_order.route('', methods=['GET', 'POST'])
def order():
    logger.info('order method')

    pack_id = request.args.get('pack', None)

    logger.info("Check subscriptions in cache")
    subscriptions = cache_service.get(key='subscriptions', prefix=session['lang_code'])
    if subscriptions is None:
        logger.info("There are no subscriptions in cache. Call billing service")
        try:
            subscriptions = rrn_billing_service.get_subscriptions(lang_code=session['lang_code'])
            logger.info("Called. Save in cache.")
            cache_service.set('subscriptions', subscriptions)
        except APIException:
            pass

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

    if pack_id is not None and subscription is None:
        # TODO think here
        raise abort(404)

    if 'order' not in session or session['order'] is None:
        # create new order
        try:
            logging.info("Creating order...")
            order_json = rrn_orders_service.create_order(status=OrderStatus.NEW)
            session['order'] = order_json
            logging.info("Order created: %s" % order_json)
        except APIException as e:
            logging.debug(e.serialize())

    return render_template('index/order.html', pack_id=pack_id, chosen_subscription=subscription,
                           subscriptions=subscriptions, code=200)
