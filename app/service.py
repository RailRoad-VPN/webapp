import logging
import sys
from http import HTTPStatus

from app.models.order_status import OrderStatus

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException, APINotFoundException

logger = logging.getLogger(__name__)


class RRNOrdersAPIService(RESTService):
    __version__ = 1

    def get_order(self, code: int = None, suuid: str = None) -> dict:
        if suuid:
            url = '%s/uuid/%s' % (self._url, suuid)
        elif code:
            url = '%s/code/%s' % (self._url, code)
        else:
            raise KeyError
        api_response = self._get(url=url)

        if api_response.is_ok:
            return api_response.data
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def create_order(self, status: OrderStatus) -> dict:
        data = {
            'status_id': status.sid
        }
        api_response = self._post(data=data)
        if api_response.is_ok and 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            if api_response.is_ok:
                return api_response.data
            else:
                logging.debug(api_response.serialize())
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_order(self, order_json: dict) -> bool:
        api_response = self._put(data=order_json)
        if api_response.is_ok and 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            if api_response.is_ok:
                return api_response.data
            else:
                logging.debug(api_response.serialize())
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)


class RRNUsersAPIService(RESTService):
    __version__ = 1

    def __init__(self, api_url: str, resource_name: str):
        super().__init__(api_url=api_url, resource_name=resource_name)

    def create_user(self, email, password) -> dict:
        user_json = {
            'email': email,
            'password': password,
        }
        api_response = self._post(data=user_json, headers=self._headers)
        if api_response.is_ok and 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            if api_response.is_ok:
                return api_response.data
            else:
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_user(self, user_json: dict) -> bool:
        url = '%s/%s' % (self._url, user_json['uuid'])
        api_response = self._put(url=url, data=user_json, headers=self._headers)
        if api_response.is_ok:
            return True
        else:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_user(self, uuid: str = None, email: str = None) -> dict:
        if uuid:
            url = '%s/uuid/%s' % (self._url, uuid)
        elif email:
            url = '%s/email/%s' % (self._url, email)
        else:
            raise KeyError
        api_response = self._get(url=url)

        if api_response.is_ok:
            return api_response.data
        elif api_response.code == HTTPStatus.NOT_FOUND:
            logger.error(api_response.serialize())
            raise APINotFoundException(http_code=api_response.code, errors=api_response.errors)
        else:
            logger.error(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_user_subscription(self, user_uuid: str, subscription_uuid: str) -> dict:
        url = self._url + '/%s/subscriptions/%s' % (user_uuid, subscription_uuid)
        api_response = self._get(url=url)
        if api_response.is_ok:
            return api_response.data
        elif api_response.code == HTTPStatus.NOT_FOUND:
            raise APINotFoundException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def create_user_subscription(self, user_uuid: str, subscription_id: int, order_uuid: str) -> dict:
        data = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'order_uuid': order_uuid,
        }
        url = self._url + '/%s/subscriptions' % user_uuid
        api_response = self._post(data=data, url=url)
        if api_response.is_ok and 'Location' in api_response.headers:
            us_loc = api_response.headers.get('Location')
            api_response = self._get(url=us_loc)
            if api_response.is_ok:
                return api_response.data
            else:
                logging.debug(api_response.serialize())
                raise APIException(http_code=api_response.code, errors=api_response.errors)
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_user_subscription(self, subscription_json: dict) -> bool:
        url = self._url + '/%s/subscriptions/%s' % (subscription_json['user_uuid'], subscription_json['uuid'])
        api_response = self._put(data=subscription_json, url=url)
        if api_response.is_ok:
            return True
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)


class RRNBillingAPIService(RESTService):
    __version__ = 1

    def __init__(self, api_url: str, resource_name: str):
        super().__init__(api_url=api_url, resource_name=resource_name)

    def get_subscriptions(self, lang_code: str) -> dict:
        headers = {
            'Accept-Language': lang_code
        }

        api_response = self._get(headers=headers)

        if api_response.is_ok:
            return api_response.data
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_subscription_by_id(self, id: int, lang_code: str) -> dict:
        headers = {
            'Accept-Language': lang_code
        }

        url = "%s/%s" % (self._url, id)
        api_response = self._get(url=url, headers=headers)

        if api_response.is_ok:
            return api_response.data
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)
