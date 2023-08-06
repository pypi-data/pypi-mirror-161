from typing import Any

import requests
from requests import HTTPError

from .errors import VaultError


def store_vault_secrets(vault_url: str, token: str, secrets: dict[str, Any]) -> str:
    response = requests.post(
        vault_url,
        headers={'Authorization': f'Bearer {token}'},
        json=secrets,
    )
    try:
        response.raise_for_status()
    except HTTPError:
        raise VaultError(f'Vault Error: {response.reason}')

    return response.json()['vault']


def fetch_vault_secrets(vault_url: str, token: str) -> dict[str, Any]:
    response = requests.get(
        vault_url,
        headers={'Authorization': f'Bearer {token}'},
    )
    try:
        response.raise_for_status()
    except HTTPError:
        raise VaultError(f'Vault Error: {response.reason}')

    return response.json()
