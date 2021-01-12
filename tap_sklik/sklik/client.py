"""
A client for Sklik API: https://api.sklik.cz/drak/

Sklik API is a XML-RPC API, but they support HTTP JSON as an alternative where
method is the route and parameters are in a JSON payload
"""

from typing import Any, Dict, List
import requests

SKLIK_API_URL = "https://api.sklik.cz/drak/json/v5"


def _post_sklik(method: str, arguments: List[Any]) -> Dict[str, Any]:
    """
    Helper to post to Sklik (and handle response status)

    Raises an Exception if request failed
    """
    # request url is base URL joined with the method requested (e.g. `ads.list`)
    request_url = SKLIK_API_URL + ("/" if not method.startswith("/") else "") + method

    response = requests.post(url=request_url, json=arguments)

    if response.status_code != 200:
        raise Exception(
            f"Could not request {request_url}: status code {response.status_code}",
            request_url,
            arguments,
            response,
        )

    response_data = response.json()

    response_data_status = response_data.get("status", None)
    if response_data_status != 200:
        response_data_status_message = response_data.get("statusMessage", None)
        raise Exception(
            f"API call {request_url} failed: status code {response_data_status}"
            + f"({response_data_status_message})",
            request_url,
            arguments,
            response_data,
        )

    return response_data


def _sklik_login(token: str) -> str:
    """
    Get a Sklik session from a token

    Raises an Exception if request failed or if the response holds no session
    """
    response_data = _post_sklik("client.loginByToken", [token])
    maybe_session = response_data.get("session", None)

    if maybe_session is None:
        raise Exception("No session provided by Sklik response on login")
    else:
        return maybe_session


class Client:
    def __init__(self, token: str) -> None:
        self.token = token
        self.session = _sklik_login(token)

    def call(self, method: str, arguments: List[Any]) -> Dict[str, Any]:
        """
        Send an API call to Sklik via HTTP/JSON API, with handled authentication.
        Raises an Exception if API call failed.
        """
        arguments_with_auth = [{"session": self.session}, *arguments]
        return _post_sklik(method, arguments_with_auth)
