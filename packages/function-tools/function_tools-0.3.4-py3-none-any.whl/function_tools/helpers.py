from typing import (
    Optional,
    Type,
    Union,
)

from function_tools.caches import (
    BaseCache,
    CacheStorage,
)


class BaseHelper:
    """
    Базовый класс помощника. Предполагается, что у наследников будут
    создаваться кеши и собираться прочая вспомогательная информация, которая
    требуется для исполнения действий
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

        self._cache_class = self._prepare_cache_class()

        self._cache: Union[Optional[BaseCache], Optional[CacheStorage]] = None

        self._prepare_cache(*args, **kwargs)

    @property
    def cache(self):
        """
        Возвращает кеш помощника
        """
        return self._cache

    def _prepare_cache_class(self) -> Union[Optional[Type[BaseCache]], Optional[Type[CacheStorage]]]:
        """
        Возвращает класс кеша помощника
        """
        return BaseCache

    def _prepare_cache(self, *args, **kwargs):
        """
        Метод создания кеша.

        Кеш хранится в публичном свойстве cache. По умолчанию добавлена
        заглушка.
        """
        if issubclass(self._cache_class, (BaseCache, CacheStorage)):
            self._cache = self._cache_class(*args, **kwargs)
        else:
            self._cache = BaseCache(*args, **kwargs)


class BaseRunnerHelper(BaseHelper):
    """
    Базовый класс помощника ранера выполнения функций
    """


class BaseFunctionHelper(BaseHelper):
    """
    Базовый класс помощника функции. Предполагается, что в наследниках будут
    создаваться кеши и собираться прочая вспомогательная информация, которая
    требуется для исполнения функции
    """
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
