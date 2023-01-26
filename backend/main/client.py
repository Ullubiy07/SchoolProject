import asyncio
import selectors
from typing import Optional

from httpx import AsyncClient, Response
from SchoolProject.settings import DSS_SERVER_URL
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class SignatureSpec:
    name: str
    box: tuple[int, int, int, int]
    credential_id: str


def _extract_document_id(response: Response):
    body = response.json()

    print(body)
    return body["document_id"]


def create_request_params(signature_spec, filename):
    return {
        "signatures_specs": signature_spec,
        "document_id": filename
    }


class SigningException(Exception):
    pass


class DssClient:
    def __init__(self, http_client: Optional[AsyncClient] = None, url: str = DSS_SERVER_URL):
        self.http_client = http_client or AsyncClient()
        self.url = url
        self.upload_url = self.url + "/dss/v1/upload/"
        self.sign_document_url = self.url + "/dss/v1/sign_docx/"

        self.loop = asyncio.new_event_loop()

    def sign_docx_document(self, document: bytes, *specs) -> bytes:
        return self.loop.run_until_complete(self.async_sign_docx_document(document, *specs))

    async def async_sign_docx_document(self, document: bytes, *specs) -> bytes:
        document_id = self._upload_file(document)

        signature_specs = [asdict(spec) for spec in specs]

        response = await self.http_client.post(
            url=self.sign_document_url,
            json=create_request_params(
                signature_specs,
                _extract_document_id(await document_id)
            ),
            timeout=None
        )

        if response.status_code == 200:
            return response.content

        raise SigningException(response.status_code)

    async def _upload_file(self, document: bytes):
        return await self.http_client.post(
            url=self.upload_url,
            files=[("file", document), ],
            headers={
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
