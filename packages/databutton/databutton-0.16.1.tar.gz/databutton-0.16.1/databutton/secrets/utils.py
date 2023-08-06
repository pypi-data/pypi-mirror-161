import base64


def bytes_to_base64str(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf8")


def base64str_to_bytes(value_base64: str) -> bytes:
    return base64.urlsafe_b64decode(value_base64)
