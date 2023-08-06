from abc import (
    ABCMeta,
    abstractmethod,
)
from collections import (
    deque,
)
from typing import (
    Deque,
    Type,
)

from django.db import (
    transaction,
)
from django.db.models import (
    Model,
)

from function_tools.mixins import (
    RegisteredEntityMixin,
    ValidatorMixin,
)
from function_tools.results import (
    BaseRunnableResult,
)
from function_tools.utils import (
    rebind_model_rel_id,
)
from function_tools.validators import (
    BaseValidator,
)


class RunnableObject(
    ValidatorMixin,
    RegisteredEntityMixin,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов выполняемых объектов
    """

    def __init__(self, *args, **kwargs):
        self._validator: BaseValidator = self._prepare_validator(*args, **kwargs)
        self._result: BaseRunnableResult = self._prepare_result(*args, **kwargs)

    def _prepare_result_class(self) -> Type[BaseRunnableResult]:
        """
        Возвращает класс результата работы ранера
        """
        return BaseRunnableResult

    @property
    def result(self) -> BaseRunnableResult:
        return self._result

    def _prepare_result(self, *args, **kwargs):
        """
        Метод подготовки результата
        """
        result_class = self._prepare_result_class()

        if issubclass(result_class, BaseRunnableResult):
            result = result_class(*args, **kwargs)
        else:
            result = BaseRunnableResult(*args, **kwargs)

        return result

    def adopt_prev_runnable_result(self, prev_runnable_result):
        """Метод перенимания результата предыдущего ранера."""
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Метод запуска выполняемого объекта
        """


class LazySavingRunnableObject(
    RunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов с отложенным сохранением

    Функции или другие исполняемые объекты должны иметь возможность быть
    атомарными. Для достижения этой цели необходимо все
    действия по сохранению выполнять в транзакции. Если сохранение
    объектов моделей производится непосредственно в коде, то возникает
    ситуация, когда транзакции становятся длинными. По логике вещей, в
    транзанзакцию должны быть обернуты действия на сохранение объектов. Это
    достигается с помощью предоставляемого функционала. В процессе работы
    функции не производится сохранение объектов модели, а они складываются в
    очередь на сохранение. Создаваемые объекты используются в качестве внешних
    объектов, как и ранее. После выполнения всех действий вызывается метод
    do_save, который открывает транзакцию и выполняет все запланированные на
    выполнение действия в порядке добавления в очередь.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue_to_save: Deque = deque()

    def do_on_save(self, object_):
        """
        Метод добавления объекта в очередь на сохранение
        """
        self._queue_to_save.append(object_)

    @abstractmethod
    def _do_save_objects_queue(self):
        """
        Выполенение сохранения объектов из очереди
        """

    def do_save(self):
        """
        Выполнение действий сохранения объектов из очереди в транзакции
        """
        with transaction.atomic(savepoint=False):
            self._do_save_objects_queue()


class LazySavingActionModelRunnableObject(
    LazySavingRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный для создания классов исполняемых объектов с отложенным сохранением, использующих в качестве объектов
    объекты моделей и функции как действия. Обычно функции - это замыкания.
    """
    def _do_save_objects_queue(self):
        """
        Выполенение сохранения объектов из очереди
        """
        while self._queue_to_save:
            x = self._queue_to_save.popleft()

            if callable(x):
                x()
            else:
                if isinstance(x, Model):
                    rebind_model_rel_id(x)
                    x.save()
