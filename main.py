import requests
import json


def login(email: str, password: str) -> str:
    r = requests.post(
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyDlmqEmT_xyn91XrDmJqSlXTTnN_DcTFAk",
        json={
            "returnSecureToken": True,
            "email": email,
            "password": password,
            "clientType": "CLIENT_TYPE_WEB"})

    return r.json()


def refresh_token(refresh_token: str) -> str:
    pass


if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
