import time

from typing import Optional, Any


class MemoryCache:
    """
    Класс, реализующий хранение значения в памяти
    """
    memory_cache = {}
    _time_dict = {}

    def __init__(self, expired_timeout: Optional[float] = 300):
        """
        expired_timeout - время устаревания кэша по умолчанию, в секундах.
        По умолчанию 300 секунд (5 минут). Вы можете установить expired_timeout в None, тогда кэш никогда не устареет.
        Если указать 0, все ключи будут сразу устаревать (таким образом, можно заставить «не кэшировать»).
        """
        self.expired_timeout = expired_timeout

    def set_value(self, cache_key: str, cache_value: Any) -> None:
        """ Установка значения """
        if cache_key in self.memory_cache:
            self.memory_cache.pop(cache_key)

        self.memory_cache[cache_key] = cache_value
        self._set_expiration_time(cache_key)

    def get_value(self, cache_key: str) -> Optional[Any]:
        """ Получение значения """
        if not self._key_is_expired(cache_key):
            result = self.memory_cache.get(cache_key, {})
            return result

        return None

    def _key_is_expired(self, cache_key: str) -> bool:
        """ Проверка срока жизни ключа """
        if self.expired_timeout is None:
            return False

        if self.expired_timeout == 0:
            return True

        if cache_key in self._time_dict:
            return time.time() > self._time_dict[cache_key]

        return True

    def _set_expiration_time(self, cache_key: str):
        """ Установка времени устаревания ключа """
        self._time_dict[cache_key] = time.time() + self.expired_timeout
