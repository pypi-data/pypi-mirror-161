from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    List,
    Optional,
)

from django.utils.decorators import (
    classproperty,
)

from function_tools.caches import (
    CacheStorage,
)
from function_tools.errors import (
    BaseError,
)
from function_tools.functions import (
    BaseFunction,
    LazyDelegateSavingPredefinedQueueFunction,
    LazySavingPredefinedQueueFunction,
)
from function_tools.helpers import (
    BaseFunctionHelper,
    BaseRunnerHelper,
)
from function_tools.managers import (
    RunnerManager,
)
from function_tools.mixins import (
    RegisteredEntityMixin,
)
from function_tools.presenters import (
    ResultPresenter,
)
from function_tools.results import (
    BaseRunnableResult,
)
from function_tools.runners import (
    BaseRunner,
    LazySavingRunner,
)
from function_tools.validators import (
    BaseValidator,
)


class FunctionImplementationStrategy(
    RegisteredEntityMixin,
    metaclass=ABCMeta,
):
    """
    Базовый класс стратегии реализации функции.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._manager_class = None
        self._runner_class = None
        self._function_class = None
        self._runner_helper_class = None
        self._function_helper_class = None
        self._runner_validator_class = None
        self._function_validator_class = None
        self._runner_cache_storage_class = None
        self._function_cache_storage_class = None
        self._error_class = None
        self._runner_result_class = None
        self._function_result_class = None
        self._result_presenter_class = None

        self._prepare()

    @classproperty
    def key(cls) -> Optional[str]:
        """
        Возвращает уникальный идентификатор стратегии создания функции.
        """
        return cls._prepare_key()

    @classproperty
    def title(cls) -> Optional[str]:
        """
        Возвращает название стратегии создания функции.
        """
        return cls._prepare_title()

    @classproperty
    def function_template_name(cls) -> Optional[str]:
        """
        Возвращает наименование стратегии реализации функции.
        """
        return cls._prepare_function_template_name()

    @property
    def manager_class(self):
        return self._manager_class

    @property
    def manager_class_name(self):
        return self._manager_class.__name__

    @property
    def manager_class_module(self):
        return self._manager_class.__module__

    @property
    def runner_class(self):
        return self._runner_class

    @property
    def runner_class_name(self):
        return self._runner_class.__name__

    @property
    def runner_class_module(self):
        return self._runner_class.__module__

    @property
    def function_class(self):
        return self._function_class

    @property
    def function_class_name(self):
        return self._function_class.__name__

    @property
    def function_class_module(self):
        return self._function_class.__module__

    @property
    def runner_helper_class(self):
        return self._runner_helper_class

    @property
    def runner_helper_class_name(self):
        return self._runner_helper_class.__name__

    @property
    def runner_helper_class_module(self):
        return self._runner_helper_class.__module__

    @property
    def function_helper_class(self):
        return self._function_helper_class

    @property
    def function_helper_class_name(self):
        return self._function_helper_class.__name__

    @property
    def function_helper_class_module(self):
        return self._function_helper_class.__module__

    @property
    def runner_validator_class(self):
        return self._runner_validator_class

    @property
    def runner_validator_class_name(self):
        return self._runner_validator_class.__name__

    @property
    def runner_validator_class_module(self):
        return self._runner_validator_class.__module__

    @property
    def function_validator_class(self):
        return self._function_validator_class

    @property
    def function_validator_class_name(self):
        return self._function_validator_class.__name__

    @property
    def function_validator_class_module(self):
        return self._function_validator_class.__module__

    @property
    def runner_cache_storage_class(self):
        return self._runner_cache_storage_class

    @property
    def runner_cache_storage_class_name(self):
        return self._runner_cache_storage_class.__name__

    @property
    def runner_cache_storage_class_module(self):
        return self._runner_cache_storage_class.__module__

    @property
    def function_cache_storage_class(self):
        return self._function_cache_storage_class

    @property
    def function_cache_storage_class_name(self):
        return self._function_cache_storage_class.__name__

    @property
    def function_cache_storage_class_module(self):
        return self._function_cache_storage_class.__module__

    @property
    def error_class(self):
        return self._error_class

    @property
    def error_class_name(self):
        return self._error_class.__name__

    @property
    def error_class_module(self):
        return self._error_class.__module__

    @property
    def runner_result_class(self):
        return self._runner_result_class

    @property
    def runner_result_class_name(self):
        return self._runner_result_class.__name__

    @property
    def runner_result_class_module(self):
        return self._runner_result_class.__module__

    @property
    def function_result_class(self):
        return self._function_result_class

    @property
    def function_result_class_name(self):
        return self._function_result_class.__name__

    @property
    def function_result_class_module(self):
        return self._function_result_class.__module__

    @property
    def result_presenter_class(self):
        return self._result_presenter_class

    @property
    def result_presenter_class_name(self):
        return self._result_presenter_class.__name__

    @property
    def result_presenter_class_module(self):
        return self._result_presenter_class.__module__

    @classmethod
    @abstractmethod
    def _prepare_key(cls) -> Optional[str]:
        """
        Формирование уникального ключа стратегии создания функции.
        """

    @classmethod
    @abstractmethod
    def _prepare_title(cls) -> Optional[str]:
        """
        Формирование наименования стратегии создания функции.
        """

    @classmethod
    @abstractmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """
        Формирование названия шаблона создания функции.
        """

    def _prepare_manager_class(self):
        """
        Устанавливает класс менеджера.
        """
        self._manager_class = RunnerManager

    def _prepare_runner_class(self):
        """
        Устанавливает класс пускателя.
        """
        self._runner_class = BaseRunner

    def _prepare_function_class(self):
        """
        Устанавливает класс Функции.
        """
        self._function_class = BaseFunction

    def _prepare_runner_helper_class(self):
        """
        Устанавливает класс помощника ранера.
        """
        self._runner_helper_class = BaseRunnerHelper

    def _prepare_function_helper_class(self):
        """
        Устанавливает класс помощника функции.
        """
        self._function_helper_class = BaseFunctionHelper

    def _prepare_runner_validator_class(self):
        """
        Устанавливает класс валидатора ранера.
        """
        self._runner_validator_class = BaseValidator

    def _prepare_function_validator_class(self):
        """
        Устанавливает класс валидатора функции.
        """
        self._function_validator_class = BaseValidator

    def _prepare_runner_cache_storage_class(self):
        """
        Устанавливает класс хранилища кешей ранера.
        """
        self._runner_cache_storage_class = CacheStorage

    def _prepare_function_cache_storage_class(self):
        """
        Устанавливает класс хранилища кешей функции.
        """
        self._function_cache_storage_class = CacheStorage

    def _prepare_error_class(self):
        """
        Устанавливает класс ошибки.
        """
        self._error_class = BaseError

    def _prepare_runner_result_class(self):
        """
        Устанавливает класс результата.
        """
        self._runner_result_class = BaseRunnableResult

    def _prepare_function_result_class(self):
        """
        Устанавливает класс результата.
        """
        self._function_result_class = BaseRunnableResult

    def _prepare_result_presenter_class(self):
        """
        Устанавливает класс презентера результата.
        """
        self._result_presenter_class = ResultPresenter

    def _prepare(self):
        """
        Подготовка компонентов реализации функции.
        """
        self._prepare_manager_class()
        self._prepare_runner_class()
        self._prepare_function_class()
        self._prepare_runner_helper_class()
        self._prepare_function_helper_class()
        self._prepare_runner_validator_class()
        self._prepare_function_validator_class()
        self._prepare_function_cache_storage_class()
        self._prepare_runner_cache_storage_class()
        self._prepare_error_class()
        self._prepare_runner_result_class()
        self._prepare_function_result_class()
        self._prepare_result_presenter_class()


class SyncBaseRunnerBaseFunctionImplementationStrategy(FunctionImplementationStrategy):
    """
    Реализация простой функции без отложенного сохранения.
    """

    @classmethod
    def _prepare_uuid(cls):
        """
        Получение UUID класса. Используется при регистрации сущности в базе данных.

        Если ничего не возвращает, то регистрация в БД не будет произведена.
        """
        return '89438366-8cd7-4644-9292-1cd779fef1c0'

    @classmethod
    def _prepare_verbose_name(cls) -> str:
        """
        Полное наименование для дальнейшей регистрации и отображения пользователю.
        """
        return 'Реализация простой функции без отложенного сохранения.'

    @classmethod
    def _prepare_tags(cls) -> List[str]:
        """
        Список тегов, по которым сущность можно будет осуществлять поиск.
        """
        return []

    @classmethod
    def _prepare_key(cls) -> str:
        """
        Возвращает уникальный идентификатор стратегии создания функции.
        """
        return 'SYNC_BASE_FUNCTION'

    @classmethod
    def _prepare_title(cls) -> str:
        """
        Возвращает название стратегии создания функции.
        """
        return 'Реализация простой функции без отложенного сохранения'

    @classmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """
        Формирование названия шаблона создания функции.
        """
        return 'function_sync_template'


class SyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy(FunctionImplementationStrategy):
    """
    Реализация функции с отложенным сохранением и предустановленной очередью объектов на сохранение.
    """

    @classmethod
    def _prepare_uuid(cls):
        """
        Получение UUID класса. Используется при регистрации сущности в базе данных.

        Если ничего не возвращает, то регистрация в БД не будет произведена.
        """
        return '30583e29-3e1b-4741-ba5f-2cbeafb24eba'

    @classmethod
    def _prepare_verbose_name(cls) -> str:
        """
        Полное наименование для дальнейшей регистрации и отображения пользователю.
        """
        return 'Реализация функции с отложенным сохранением и предустановленной очередью объектов на сохранение'

    @classmethod
    def _prepare_tags(cls) -> List[str]:
        """
        Список тегов, по которым сущность можно будет осуществлять поиск.
        """
        return []

    @classmethod
    def _prepare_key(cls) -> str:
        """
        Возвращает уникальный идентификатор стратегии создания функции.
        """
        return 'SYNC_LAZY_SAVING_FUNCTION'

    @classmethod
    def _prepare_title(cls) -> str:
        """
        Возвращает название стратегии создания функции.
        """
        return (
            'Реализация функции с отложенным сохранением и предустановленной очередью объектов на сохранение. '
            'Сохранение производится после удачной работы функции'
        )

    @classmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """
        Формирование названия шаблона создания функции.
        """
        return 'function_sync_template'

    def _prepare_function_class(self):
        """
        Устанавливает класс Функции
        """
        self._function_class = LazySavingPredefinedQueueFunction


class SyncLazySavingRunnerLazyDelegateSavingPredefinedQueueFunctionImplementationStrategy(FunctionImplementationStrategy):
    """
    Реализация функции с отложенным сохранением его делегированием ранеру. Когда все функции отработают, только
    после этого запускается сохранение объектов из очередей каждой функции.
    """

    @classmethod
    def _prepare_uuid(cls):
        """
        Получение UUID класса. Используется при регистрации сущности в базе данных.

        Если ничего не возвращает, то регистрация в БД не будет произведена.
        """
        return 'df704a13-178a-4f60-a6bd-e54dac292293'

    @classmethod
    def _prepare_verbose_name(cls) -> str:
        """
        Полное наименование для дальнейшей регистрации и отображения пользователю.
        """
        return 'Реализация функции с отложенным сохранением его делегированием ранеру'

    @classmethod
    def _prepare_tags(cls) -> List[str]:
        """
        Список тегов, по которым сущность можно будет осуществлять поиск.
        """
        return []

    @classmethod
    def _prepare_key(cls) -> str:
        """
        Возвращает уникальный идентификатор стратегии создания функции.
        """
        return 'SYNC_LAZY_SAVING_RUNNER_FUNCTION'

    @classmethod
    def _prepare_title(cls) -> str:
        """
        Возвращает название стратегии создания функции.
        """
        return (
            'Реализация функции с отложенным сохранением его делегированием пускателю. Когда все функции отработают, '
            'только после этого запускается сохранение объектов из очередей каждой функции'
        )

    @classmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """
        Формирование названия шаблона создания функции.
        """
        return 'function_sync_template'

    def _prepare_runner_class(self):
        """
        Устанавливает класс ранера.
        """
        self._runner_class = LazySavingRunner

    def _prepare_function_class(self):
        """
        Устанавливает класс функции.
        """
        self._function_class = LazyDelegateSavingPredefinedQueueFunction
