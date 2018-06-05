import sys

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException
from response import APIResponse, APIResponseStatus


class RRNUsersAPIService(RESTService):

    def __init__(self, api_url: str, resource_name: str):
        super().__init__(api_url=api_url, resource_name=resource_name)

    def create_user(self, user_json: dict) -> APIResponse:
        api_response = self._post(data=user_json, headers=self._headers)
        return api_response

    def update_user(self, user_json: dict):
        url = '%s/uuid/%s' % (self._url, user_json['uuid'])
        api_response = self._put(url=url, data=user_json, headers=self._headers)
        return api_response

    def get_user(self, uuid: str = None, email: str = None) -> APIResponse:
        if uuid:
            url = '%s/uuid/%s' % (self._url, uuid)
        elif email:
            url = '%s/email/%s' % (self._url, email)
        else:
            raise KeyError
        api_response = self._get(url=url)

        return api_response


class RRNBillingAPIService(RESTService):

    def __init__(self, api_url: str, resource_name: str):
        super().__init__(api_url=api_url, resource_name=resource_name)

    def get_subscriptions(self, lang_code: str) -> APIResponse:
        headers = {
            'Accept-Language': lang_code
        }

        api_response = self._get(headers=headers)

        if api_response.status == APIResponseStatus.success.value:
            return api_response.data
        else:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_subscription_by_id(self, id: int) -> APIResponse:
        url = "%s/%s" % (self._url, id)
        api_response = self._get(url=url)

        if api_response.status == APIResponseStatus.success.value:
            return api_response.data
        else:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
