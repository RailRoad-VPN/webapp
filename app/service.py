import sys

sys.path.insert(0, '../rest_api_library/app')
from services.rest import RESTService
from services.response import APIResponse


class RailRoadAPIService(RESTService):

    _user_resource_uri = 'users'

    def __init__(self, api_url: str):
        super().__init__(api_url)

    def create_user(self, user_json: dict) -> APIResponse:
        url = "%s/%s" % (self._url, self._user_resource_uri)
        api_response = self._post(url=url, data=user_json, headers=self._headers)
        return api_response

    def update_user(self, user_json: dict):
        url = '%s/%s/uuid/%s' % (self._url, self._user_resource_uri, user_json['uuid'])
        api_response = self._put(url=url, data=user_json, headers=self._headers)
        return api_response

    def get_user(self, uuid: str = None, email: str = None) -> APIResponse:
        if uuid:
            url = '%s/%s/uuid/%s' % (self._url, self._user_resource_uri, uuid)
        elif email:
            url = '%s/%s/email/%s' % (self._url, self._user_resource_uri, email)
        else:
            raise KeyError
        api_response = self._get(url=url)

        return api_response