from dataclasses import dataclass
from typing import Optional

import hvac

from vtb_secret_utils.cache import MemoryCache


@dataclass
class VaultConfig:
    """ Конфигурация подключения к Vault """
    url: str
    role_id: str
    secret_id: Optional[str] = None
    ssl_verify: Optional[bool] = False


class VaultError(Exception):
    """ VaultError """


class VaultStorage:
    """ Интеграция с Vault """

    def __init__(self, config: VaultConfig, cache: Optional = None):
        self.cache = cache or MemoryCache()
        self.config = config
        self.client = hvac.Client(
            url=config.url,
            verify=config.ssl_verify,
        )

    def login(self) -> None:
        """
        Login с участием app role
        :return:
        """
        if not self.client.is_authenticated():
            self.client.auth.approle.login(
                role_id=self.config.role_id,
                secret_id=self.config.secret_id,
            )

    def get_secret(self, path: str) -> dict:
        """
        Получение секрета
        :param path: путь до секрета
        :return: словарь секретов
        """
        secrets = self.cache.get_value(path)
        if not secrets:
            self.login()
            response_secret = self.client.read(path)

            if not response_secret:
                raise VaultError(f'Secret not found for path {path}')

            secrets = _get_response_data(response_secret)

            self.cache.set_value(path, secrets)

        return secrets


def _get_response_data(response_secret):
    data = response_secret['data']
    if 'data' in data:
        data = data['data']
    return data
