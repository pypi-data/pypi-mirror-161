import json
from http import client
from http.client import HTTPResponse
from typing import List

from hrthy_core.http.settings import get_http_settings
from hrthy_core.security.security import generate_jwt_token, RequesterType, Requester


class Client:
    def __init__(self, host: str, port: int = 80, timeout: int = 5) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout

    @classmethod
    def _get_headers(cls, requester: Requester, scopes: List[str] = None):
        jwt = generate_jwt_token(
            requester.requester_id,
            RequesterType.service,
            scopes=scopes or [],
            company_id=requester.company_id,
            role_id=requester.role_id
        )
        return {
            'X-CloudFront-Secret-Key': get_http_settings().cloudfront_secret,
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + jwt
        }

    @classmethod
    def _handle_response(cls, connection) -> dict:
        response: HTTPResponse = connection.getresponse()
        if response.status < 200 or response.status > 299:
            raise client.HTTPException(response.status)
        return json.loads(response.read().decode())

    def _get(self, requester: Requester, url: str, data: dict = None, scopes: List[str] = None):
        headers = Client._get_headers(requester=requester, scopes=scopes)
        connection = client.HTTPConnection(host=self.host, port=self.port, timeout=self.timeout)
        connection.request(method="GET", url=url, headers=headers, body=json.dumps(data) if data is not None else None)
        return Client._handle_response(connection)
