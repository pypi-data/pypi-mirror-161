import yaml

from databutton.utils import get_project_directory

from .utils import base64str_to_bytes, bytes_to_base64str


class SecretsFileClient:
    def __init__(self, secrets_filename=None):
        if secrets_filename is None:
            secrets_filename = get_project_directory() / "databutton-secrets.yaml"
        self._secrets_filename = secrets_filename

    def _read_local_secrets(self) -> dict:
        try:
            # Could also support a secrets directory with
            # files named as keys and containing the values,
            # that's what we'll do for the docker mounting thing?
            with open(self._secrets_filename, "r") as f:
                secrets = yaml.safe_load(f)
            return secrets or {}
        except FileNotFoundError:
            return {}

    def add(self, name: str, value: bytes) -> bool:
        secrets = self._read_local_secrets()
        secrets[name] = bytes_to_base64str(value)
        with open(self._secrets_filename, "w") as f:
            yaml.safe_dump(secrets, f)
        return True

    def delete(self, name: str) -> bool:
        secrets = self._read_local_secrets()
        if name in secrets:
            del secrets[name]
        with open(self._secrets_filename, "w") as f:
            yaml.safe_dump(secrets, f)
        return True

    def get_as_base64(self, name: str) -> str:
        """Get base64 encoding of secret value."""
        return self._read_local_secrets()[name]

    def get_as_bytes(self, name: str) -> bytes:
        """Get secret value as raw bytes."""
        return base64str_to_bytes(self.get_as_base64(name))

    def get_as_text(self, name: str) -> str:
        """Get secret value as text."""
        return self.get_as_bytes(name).decode("utf8")

    def list(self) -> list[str]:
        return sorted(self._read_local_secrets().keys())
