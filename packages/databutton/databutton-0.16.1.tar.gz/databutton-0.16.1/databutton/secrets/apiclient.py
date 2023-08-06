import os

import requests

from databutton.utils import get_api_url, get_auth_token, get_databutton_config

from .utils import base64str_to_bytes, bytes_to_base64str


class SecretsApiClient:
    def __init__(self, project_id: str = None):
        if project_id is None:
            project_id = get_databutton_config().uid
        self.base_url = get_api_url(project_id) + "/secrets"
        self.project_id = project_id

    def _headers(self):
        token = get_auth_token()
        if token is None or token == "":
            raise EnvironmentError(
                "Missing auth token. Are you logged in to databutton?"
            )
        return {
            "Authorization": f"Bearer {token}",
            "x-databutton-release": os.environ.get("DATABUTTON_RELEASE"),
            "x-project-id": self.project_id,
            # TODO: rename to x-databutton-project-id everywhere else then remove
            "x-databutton-project-id": self.project_id,
        }

    def add(self, name: str, value: bytes) -> bool:
        # Note: Api expects base64 encoding of the raw bytes.
        res = requests.post(
            self.base_url + "/add",
            headers=self._headers(),
            json={"name": name, "value": bytes_to_base64str(value)},
        )
        if not res.ok:
            raise Exception("Failed to add secret")
        body = res.json()
        return body["name"] == name and body["added"] is True

    def delete(self, name: str) -> bool:
        res = requests.post(
            self.base_url + "/delete",
            headers=self._headers(),
            json={"name": name},
        )
        if not res.ok:
            raise Exception("Failed to delete secret")
        body = res.json()
        return body["name"] == name and body["deleted"] is True

    def _get_secret_data(self, name: str) -> dict:
        """Get secret value and metadata.

        Note: Returning value as field in json object such that we
        can easily include more metadata in the response if we want.
        This means the secret bytes must be formatted as a valid string,
        so we're using base64 for the transfer.
        """
        # Using post to pass parameters in body
        res = requests.post(
            self.base_url + "/get",
            headers=self._headers(),
            json={"name": name},
        )
        if not res.ok:
            raise Exception("Failed to read secret")
        return res.json()

    def get_as_base64(self, name: str) -> str:
        """Get base64 encoding of secret value."""
        return self._get_secret_data(name).get("value")

    def get_as_bytes(self, name: str) -> bytes:
        """Get secret value as raw bytes."""
        return base64str_to_bytes(self.get_as_base64(name))

    def get_as_text(self, name: str) -> str:
        """Get secret value as text."""
        return self.get_as_bytes(name).decode("utf8")

    def list(self) -> list[str]:
        res = requests.get(
            self.base_url + "/list",
            headers=self._headers(),
        )
        if not res.ok:
            raise Exception("Failed to list secrets")
        body = res.json()
        return sorted(body["secrets"])
