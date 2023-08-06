import requests
from typing import Union, List, Any, Dict
from http import HTTPStatus

from fluidtopics.markdown.errors import MD2FTError

JSONDict = Dict[str, Any]
JSONType = Union[str, List[Any], JSONDict]


class FTSession:
    """Object representing a Fluitopics Session.
    This can be used to authenticate to FT and send request to th KHUB
    """
    def __init__(self, portal_base_url: str):
        self.portal_base_url = portal_base_url.rstrip("/")
        self._session = requests.Session()

    def login(self, user: str, password: str) -> None:
        """Login to an FT portal using standard user/password"""
        login_url = self.portal_base_url + "/api/authentication/login"
        rep = self._session.post(login_url, json={"login": user, "password": password})
        if not rep.ok:
            raise MD2FTError(
                f"Cannot log in to FT portal {login_url} (user={user}, password=XXX): {rep.content}"
            )

    def set_api_key(self, token: str):
        """Set FT API Key for further request use"""
        self._session.headers['Authorization'] = f"Bearer {token}"
        # Try accessing khub locale in order to check token validity
        try:
            self.head("/api/khub/locales")
        except MD2FTError as e:
            raise MD2FTError("API Key token is invalid.") from e

    def _check_status(self, resp):
        if resp.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
            raise MD2FTError(
                f"Server rejected credentials as Unauthorized ({resp.status_code})."
            )
        elif resp.status_code == HTTPStatus.NOT_FOUND:
            raise MD2FTError(
                f'FT API call "{resp.url}" answered not found ({resp.status_code}).'
            )
        elif not resp.ok:
            raise MD2FTError(resp.text)

    def request(
        self,
        object_path: str,
        method: str = "GET",
        json_result=True,
        check_status=True,
        **kwargs
    ) -> Union[JSONType, requests.Response, None]:
        query = f"{self.portal_base_url}{object_path}"

        resp = self._session.request(
            method,
            query,
            **kwargs
        )
        if check_status:
            self._check_status(resp)
        if json_result:
            return resp.json() if resp.text else None
        else:
            return resp

    def get(self, object_path, **kwargs):
        return self.request(object_path, method="GET", **kwargs)

    def head(self, object_path, **kwargs):
        return self.request(object_path, method="HEAD", **kwargs)

    def post(self, object_path, **kwargs):
        return self.request(object_path, method="POST", **kwargs)

    def delete(self, object_path, **kwargs):
        return self.request(object_path, method="DELETE", **kwargs)

    def put(self, object_path, **kwargs):
        return self.request(object_path, method="PUT", **kwargs)
