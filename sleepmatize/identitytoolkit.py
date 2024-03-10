import requests
import json


class LoginException(Exception):
    pass


class IdentityToolkitHelper:
    def __init__(self, api_key: str, request_origin: str = "https://mathmatize.com"):
        self.api_key = api_key
        self.base_url = "https://identitytoolkit.googleapis.com/v1"

        self.session = requests.Session()
        self.session.headers["Origin"] = request_origin

        self.id_token = ""
        self.refresh_token = ""

    def _make_request(self, endpoint: str, method: str = "get", *args, **kwargs) -> dict:
        request_method = getattr(self.session, method)
        request_url = f"{self.base_url}/{endpoint}?key={self.api_key}"

        r = request_method(request_url, *args, **kwargs)

        return r.json()

    def sign_in(self, email: str, password: str) -> bool:
        json_response = self._make_request("accounts:signInWithPassword",
                                           json={
                                               "returnSecureToken": True,
                                               "email": email,
                                               "password": password,
                                               "clientType": "CLIENT_TYPE_WEB"}, method="post")

        if 'idToken' not in json_response:
            raise LoginException(
                "Recieved invalid response from API:\n" + json.dumps(json_response, indent=4))

        self.id_token = json_response["idToken"]
        self.refresh_token = json_response["refreshToken"]

        return json_response

    def refresh_id_token(self):
        raise NotImplementedError()
