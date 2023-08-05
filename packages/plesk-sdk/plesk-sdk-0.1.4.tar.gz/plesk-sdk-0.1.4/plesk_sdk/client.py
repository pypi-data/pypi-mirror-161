import requests
import json
from typing import Dict, List

from .patterns import Singleton


class Client(metaclass=Singleton):
    API_KEY = None

    def __init__(self, plesk_url: str, login: str, password: str) -> None:
        """
        :param plesk_ur: str - Base endpoint of Plesk Service
        :param login: str - Admin login is required for user authorization.
        :param password: str - Admin password is required for user authorization.
        :return: None
        """

        self.plesk_url = plesk_url
        self.login = login
        self.password = password
        if self.plesk_url.endswith("/"):
            self.plesk_url = self.plesk_url[:-1]
        self.headers = {"Content-Type": "application/json"}
        self.authorize()

    def request_config(self) -> Dict:
        return {"verify": False, "headers": self.get_headers()}

    def get_headers(self) -> Dict:
        if self.API_KEY:
            self.headers.update({"X-API-Key": self.API_KEY})

        return self.headers

    def get_response(self, resp: requests.Response) -> Dict:
        if not str(resp.status_code).startswith("2"):
            raise ValueError("API Error: ", resp.content)

        return resp.json()

    def authorize(self) -> None:
        resp = requests.post(
            f"{self.plesk_url}/auth/keys",
            auth=(self.login, self.password),
            data=json.dumps({}),
            **self.request_config(),
        )
        resp = self.get_response(resp=resp)
        self.API_KEY = resp["key"]

    def subscription_off(self, subscription_name: str) -> Dict:
        """
        Suspends a whole subscription.

        :param subscription_name: str - Accepts a domain name
        :return: Dict - {'code': 0, 'stdout': '', 'stderr': ''}
        """

        params = ["--webspace-off"]
        params.append(subscription_name)

        resp = requests.post(
            f"{self.plesk_url}/cli/subscription/call",
            data=json.dumps({"params": params}),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def subscription_on(self, subscription_name: str) -> Dict:
        """
        Activates a whole subscription.

        :param subscription_name:  str - Accepts a domain name
        :return: Dict - {'code': 0, 'stdout': '', 'stderr': ''}
        """

        params = ["--webspace-on"]
        params.append(subscription_name)

        resp = requests.post(
            f"{self.plesk_url}/cli/subscription/call",
            data=json.dumps({"params": params}),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def kwargs_to_list(self, kwargs: Dict) -> List[str]:
        params = []
        for item in kwargs.items():
            key, value = item
            params.extend([f"-{key}", value])

        return params

    def subscription_create(self, subscription_name: str, **kwargs) -> Dict:
        """
        Creates a subscription.

        :param subscription_name: str - Accepts a domain name
        :param kwargs: Dict - must contain subscription_name, owner, service, login, ip, passwd
        :return: -> Dict - {'code': 0, 'stdout': "SUCCESS: Creation of domain '<subscription_name>' completed.", 'stderr': ''}
        """

        params = ["--create", subscription_name]
        params.extend(self.kwargs_to_list(kwargs=kwargs))

        resp = requests.post(
            url=f"{self.plesk_url}/cli/subscription/call",
            data=json.dumps({"params": params}),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def create_customer(self, data: Dict) -> Dict:
        """
        Create a new Customer account

        :param data: Dict - must contain name, login, password, email, type, company, status, locale, owner_login, external_id, description
        :return: Dict - {'id': <id:int>, 'guid': <guid:str>}
        """

        resp = requests.post(
            url=f"{self.plesk_url}/clients",
            data=json.dumps(data),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def update_customer(self, customer_id: int, data: Dict) -> Dict:
        """
        Update a Customer account

        :para customer_id: int - unique id of Customer
        :param data: Dict - fields for changes name, login, password, email, company, status, locale, owner_login, external_id, description
        :return: Dict - {'id': <id:int>, 'guid': <guid:str>}
        """
        resp = requests.put(
            url=f"{self.plesk_url}/clients/{customer_id}",
            data=json.dumps(data),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def customer_activate(self, customer_id: int) -> Dict:
        """
        Update a Customer status to active

        :para customer_id: int - unique id of customer
        :return: Dict - {'id': <id:int>, 'guid': <guid:str>}
        """
        resp = requests.put(
            url=f"{self.plesk_url}/clients/{customer_id}",
            data=json.dumps({"status": 0}),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def customer_suspend(self, customer_id: int) -> Dict:
        """
        Update a Customer status to suspend

        :para customer_id: int - unique id of customer
        :return: Dict - {'id': <id:int>, 'guid': <guid:str>}
        """

        resp = requests.put(
            url=f"{self.plesk_url}/clients/{customer_id}",
            data=json.dumps({"status": 1}),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

    def auto_logging(self, user: str) -> Dict:
        """
        :param data: Dict - must contain user
        :return: Dict - {"code": 0,
        "stdout": "https://<server-hostname-or-ip>/login?secret=<secret>\n",
        "stderr": ""}
        """

        params = ["--get-login-link", "-user", user]

        resp = requests.post(
            url=f"{self.plesk_url}/cli/admin/call",
            data=json.dumps({"params": params}),
            **self.request_config(),
        )

        return self.get_response(resp=resp)

