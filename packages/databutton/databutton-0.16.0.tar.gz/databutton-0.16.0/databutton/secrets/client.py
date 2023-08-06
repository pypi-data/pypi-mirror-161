def get_secrets_client():
    from .apiclient import SecretsApiClient

    return SecretsApiClient()


def get_as_bytes(name: str) -> bytes:
    """Get a project secret as raw bytes."""
    return get_secrets_client().get_as_bytes(name)


def get_as_text(name: str) -> str:
    """Get project secret as string, assuming it was originally a utf8 string."""
    return get_secrets_client().get_as_text(name)
