"""
This connector simplifies http connection from Python to Microsoft Dynamics 365 Business Central platform 16.xx API
by providing 4 methods: insert, read, modify, delete (CRUD)
___________________
Dynamics 365 Business Central API documentation:
https://docs.microsoft.com/en-us/dynamics-nav/api-reference/v1.0/

Dynamics 365 Business Central API endpoints:
https://docs.microsoft.com/en-us/dynamics-nav/endpoints-apis-for-dynamics

Dynamics 365 Business Central API developing
https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-connect-apps

Dynamics 365 Business Central API filters creation like "number eq '20000'"
https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-connect-apps-filtering

Dynamics 365 Business Central API tips
https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-connect-apps-tips
___________________
"""

import requests


class Connect(object):
    """
        :param: url - API endpoint url https://docs.microsoft.com/en-us/dynamics-nav/endpoints-apis-for-dynamics
                auth - authorization for basic (user, password) or other;
                headers = {"Accept-Language": language} or any.
        :return: object
    """

    def __init__(self, url, auth=None, headers=None):
        self.url = url
        self._auth = auth
        self._headers = headers
        self.filter_text = str()  # filter_text can be modified by calling object.filter_text = new_filter
        self._etag = str()  # for internal usage
        self.except_error = None  # stores connection or other not BC error

    def read(self, filter_text=None):
        """
        reads records according filters;
        endpoint url can be changed before read
        :param : filter_text - API specific filter text 
        (https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-connect-apps-filtering)
        :return: if success (200) - value list which includes record's fields dictionary (dictionaries in list),
                 or blank list if no records in response (wrong filters) and except_error = None
                 or blank list if connection error (except_error - has error text)
                 or blank list if connected but failed in BC - except_error has [responds status code, responds message]
        """
        if filter_text is not None:  # set filter_text from parameter if it was used
            self.filter_text = filter_text
        else:
            _filter = None

        if self.filter_text is not None:
            if len(self.filter_text) > 0:
                _filter = "$filter=" + self.filter_text
            else:
                _filter = None

        try:
            # response = requests.get(self.url + __filter_url, auth=self._auth, headers=self._headers)
            response = requests.get(self.url, params=_filter, auth=self._auth, headers=self._headers)
        except requests.exceptions.ConnectionError as ex_err:
            self.except_error = ex_err
            return []

        if response.status_code != 200:  # failed
            self.except_error = [response.status_code, response.reason]
            return []

        self.filter_text = None  # remove filter after call
        response_dict = response.json()  # dict

        value_list = response_dict.get("value")  # list return
        if value_list and len(value_list) >= 1:  # if dict has key "value" then data are list
            value_dict = value_list[0]  # dict
            self._etag = value_dict.get("@odata.etag")  # already decoded - removed \
            return value_list
        else:  # if there is no key "value", then try to get etag directly
            self._etag = response_dict.get("@odata.etag", "")  # already decoded - removed \
            if self._etag == "":
                return []
            else:
                return [response_dict]

    def insert(self, json_body):
        """
        creates record specified in json_body. primary key fields values must be filled in. Except when it is created
        automatically in BC (for example by using number series, or relations). For example sales order no. is taken
        from number series so no needs to specify in json. Sales line document no is taken from sales header and
        no need to be specified.
        endpoint url can be changed before insert
        :param: json_body: dictionary(json) with primary key fields and values (mandatory)
                and other fields and values
        :return: list [201, Created] means record is created. otherwise look for error
        """

        try:
            response = requests.post(self.url, auth=self._auth, headers=self._headers, json=json_body)
        except requests.exceptions.ConnectionError as ex_err:
            self.except_error = ex_err
            return []

        if response.status_code != 201:  # failed
            self.except_error = [response.status_code, response.reason]
            return []

        return [response.status_code, response.reason]  # 201 - Created

    def modify(self, json_body):
        """
        modify record specified by id with values specified in json_body
        endpoint url can be changed before call
        record id in endpoint url is required for execution 
        for example http://.../items(5ed6d5c2-98e7-ea11-8347-cd616ef7b1aa)/
        :param json_body: json with record fields and values need to be modified
        :return: list [200, OK] means everything is OK, otherwise look for error.
        """
        response = self.read()  # just to get etag value
        if self.except_error:  # failed read connection
            return [self.except_error]

        if len(response) == 0 or self._etag == "":  # read response found no records to update
            return []

        self._headers["If-Match"] = self._etag

        response = requests.patch(self.url, auth=self._auth, headers=self._headers, json=json_body)

        return [response.status_code, response.reason]  # 200 OK

    def delete(self):
        """
        delete record specified by id
        endpoint url can be changed before call
        record id in endpoint url is required for execution 
        for example http://.../items(5ed6d5c2-98e7-ea11-8347-cd616ef7b1aa)/
        :return: list [204, No Content] means records is deleted. Otherwise something gone wrong
        or empty list if found nothing
        """
        response = self.read()
        if self.except_error:  # failed read connection
            return [self.except_error]

        if len(response) == 0 or self._etag == "":  # read response found no records to delete
            return []

        self._headers["If-Match"] = self._etag

        response = requests.delete(self.url, auth=self._auth, headers=self._headers)
        return [response.status_code, response.reason]  # 204, OK
