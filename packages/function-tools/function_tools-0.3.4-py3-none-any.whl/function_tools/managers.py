from abc import (
    ABCMeta,
)
from typing import (
    Optional,
    Type,
)

from django.utils.decorators import (
    classproperty,
)

from function_tools.mixins import (
    RegisteredEntityMixin,
)
from function_tools.runners import (
    BaseRunner,
)


class RunnerManager(
    RegisteredEntityMixin,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания менеджеров ранеров запускаемых объектов.
    Служит для добавления функций-задач, ранеров в очередь на исполнение.
    Является удобным механизмом для скрытия заполнения ранера и его запуск.
    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self._runner_class = self._prepare_runner_class()

        self._runner: Optional[BaseRunner] = None

    @property
    def result(self):
        return self._runner.result

    @classproperty
    def runner_class(cls):
        """
        Возвращает класс ранера.
        """
        return cls._prepare_runner_class()

    @classmethod
    def _prepare_runner_class(cls) -> Type[BaseRunner]:
        """
        Возвращает класс ранера.
        """
        return BaseRunner

    def _before_create_runner(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера перед созданием ранера.
        """

    def _create_runner(self, *args, **kwargs):
        """
        Метод создания ранера.
        """
        if issubclass(self._runner_class, BaseRunner):
            self._runner = self._runner_class(*args, **kwargs)
        else:
            self._runner = BaseRunner(*args, **kwargs)

    def _after_create_runner(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера после создания ранера.
        """

    def _before_prepare_runner(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера перед подготовкой ранера.
        """

    def _prepare_runner(self, *args, **kwargs):
        """
        Метод подготовки ранера к запуску.
        """

    def _after_prepare_runner(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера после подготовки ранера.
        """

    def _before_start_runner(self, *args, **kwargs):
        """
       Точка расширения поведения менеджера ранера перед запуском ранера.
       """

    def _start_runner(self, *args, **kwargs):
        """
        Точка расширения в месте запуска ранера.
        """
        if self._runner:
            self._runner.run(*args, **kwargs)

    def _after_start_runner(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера после запуска ранера.
        """

    def run(self, *args, **kwargs):
        self._before_create_runner(*args, **kwargs)
        self._create_runner(*args, **kwargs)
        self._after_create_runner(*args, **kwargs)

        self._before_prepare_runner(*args, **kwargs)
        self._prepare_runner(*args, **kwargs)
        self._after_prepare_runner(*args, **kwargs)

        self._before_start_runner(*args, **kwargs)
        self._start_runner(*args, **kwargs)
        self._after_start_runner(*args, **kwargs)


class LazySavingRunnerManager(RunnerManager):
    """
    Абстрактный класс для создания менеджеров ранеров c отложенным
    сохранением. В качестве ранера должен использоваться потомок
    LazySavingRunner.
    """

    def _before_do_save(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера перед запуском сохранения объектов.
        """

    def _do_save(self, *args, **kwargs):
        """
        Запуск сохранения ранера.
        """
        self._runner.do_save(*args, **kwargs)

    def _after_do_save(self, *args, **kwargs):
        """
        Точка расширения поведения менеджера ранера после запуска сохранения объектов.
        """

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

        self._before_do_save(*args, **kwargs)
        self._do_save(*args, **kwargs)
        self._after_do_save(*args, **kwargs)
