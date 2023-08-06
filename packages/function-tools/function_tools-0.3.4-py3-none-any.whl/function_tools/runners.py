from abc import (
    ABCMeta,
)
from collections import (
    deque,
)
from typing import (
    Deque,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from function_tools.errors import (
    BaseError,
)
from function_tools.functions import (
    LazyDelegateSavingSettableQueueFunction,
)
from function_tools.general import (
    LazySavingActionModelRunnableObject,
    LazySavingRunnableObject,
    RunnableObject,
)
from function_tools.helpers import (
    BaseHelper,
    BaseRunnerHelper,
)
from function_tools.mixins import (
    GlobalHelperMixin,
    HelperMixin,
)


class BaseRunner(
    HelperMixin,
    RunnableObject,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания ранеров выполнения запускаемых объектов.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._helper: Union[BaseHelper, BaseRunnerHelper] = self._prepare_helper(*args, **kwargs)
        self._queue: Deque[RunnableObject] = deque()

        self._populate_queue_by_runnable_classes(*args, **kwargs)

    @classmethod
    def _prepare_runnable_classes(cls) -> List[Type[RunnableObject]]:
        """
        Возвращает список классов запускаемых объектов, которые будут ставиться в очередь на исполнение.

        В текущий момент нужно явно указывать классы, но в будущем, появится возможность получения списка классов
        запускаемых сущностей в рамках ранера.
        """

    def _populate_queue_by_runnable_classes(self, *args, **kwargs):
        """
        Заполнение очереди запускаемыми объектами.
        """
        runnable_classes = self._prepare_runnable_classes()

        for runnable_class in runnable_classes:
            runnable = runnable_class(*args, **kwargs)

            self.enqueue(runnable=runnable, *args, **kwargs)

    def _prepare_runnable_before_enqueue(
        self,
        runnable: RunnableObject,
    ):
        """
        Подготовка запускаемого объекта к работе.

        В данной точке расширения можно пропатчить объект через публичные методы.
        """
        if isinstance(runnable, GlobalHelperMixin):
            runnable.set_global_helper(
                global_helper=self._helper,
            )

    def enqueue(
        self,
        runnable: Union[RunnableObject, Tuple[RunnableObject, ...]],
        *args,
        **kwargs,
    ):
        """
        Добавление задачи на выполнение функции в очередь.
        """
        if not isinstance(runnable, tuple):
            runnable = (runnable, )

        for r in runnable:
            self._prepare_runnable_before_enqueue(
                runnable=r,
            )

            self._queue.append(r)

    def _update_queue(self):
        """
        Метод позволяет обновлять очередь ранеров на ходу.
        """

    def run(self, *args, **kwargs):
        """
        Выполнение всех задач стоящих в очереди.
        """
        self.before_validate()
        self.validate()
        self.after_validate()

        if self.result.has_not_errors:
            # атрибут отвечающий за передачу результата следующему в цепочке ранеру
            prev_runnable_result = None

            self._update_queue()

            while self._queue:
                runnable: RunnableObject = (
                    self._queue.popleft()
                )

                runnable.adopt_prev_runnable_result(prev_runnable_result=prev_runnable_result)

                runnable.before_validate()
                runnable.validate()
                runnable.after_validate()

                runnable.run()

                prev_runnable_result = runnable.result

                self.result.append_entity(runnable.result)


class LazySavingRunner(
    BaseRunner,
    LazySavingRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов ранеров с отложенным сохранением объектов из очередей на сохранение
    запускаемых объектов.

    Сохранение производится, когда все запускаемые объекты очереди отработают.
    """

    def _do_save_objects_queue(self):
        """
        Запуск сохранения у выполняемых объектов.
        """
        while self._queue_to_save:
            runnable: LazySavingRunnableObject = self._queue_to_save.popleft()
            runnable.do_save()

    def run(self, *args, **kwargs):
        """
        Выполнение всех задач стоящих в очереди.
        """
        self.before_validate()
        self.validate()
        self.after_validate()

        if self.result.has_not_errors:
            # атрибут отвечающий за передачу результата следующему в цепочке ранеру
            prev_runnable_result = None

            self._update_queue()

            while self._queue:
                runnable: RunnableObject = self._queue.popleft()

                runnable.adopt_prev_runnable_result(prev_runnable_result=prev_runnable_result)

                runnable.before_validate()
                runnable.validate()
                runnable.after_validate()

                runnable.run()

                prev_runnable_result = runnable.result

                self.result.append_entity(runnable.result)

                if runnable.result.has_not_errors:
                    self._queue_to_save.append(runnable)


class LazyStrictSavingRunner(
    LazySavingRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов ранеров с отложенным сохранением объектов в строгом режиме.

    Если не все выполняемые объекты отработали корректно, то ни один не сохраняется.
    """

    def _get_strict_saving_error(self) -> BaseError:
        """
        Ошибка, которая должна быть возвращена при несоблюдении условий строгого режима.
        """
        return BaseError()

    def run(self, *args, **kwargs):
        """
        Выполнение всех задач стоящих в очереди.
        """
        self.before_validate()
        self.validate()
        self.after_validate()

        if self.result.has_not_errors:
            prev_runnable_result = None
            queue_length = len(self._queue)

            self._update_queue()

            while self._queue:
                runnable: RunnableObject = (
                    self._queue.popleft()
                )

                runnable.adopt_prev_runnable_result(prev_runnable_result=prev_runnable_result)

                runnable.before_validate()
                runnable.validate()
                runnable.after_validate()

                runnable.run()

                prev_runnable_result = runnable.result

                self.result.append_entity(runnable.result)

                if runnable.result.has_not_errors:
                    self._queue_to_save.append(runnable)

            if queue_length != len(self._queue_to_save):
                self.result.append_entity(
                    self._get_strict_saving_error()
                )

                self._queue_to_save.clear()


class GlobalHelperRunner(
    GlobalHelperMixin,
    BaseRunner,
    metaclass=ABCMeta,
):
    """
    Базовый класс для создания ранеров выполнения запускаемых объектов с глобальным помощником.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._global_helper: BaseRunnerHelper = self._prepare_global_helper(*args, **kwargs)


class LazySavingGlobalHelperRunner(
    GlobalHelperMixin,
    LazySavingRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов ранеров с отложенным сохранением объектов с глобальным помощником.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._global_helper: BaseRunnerHelper = self._prepare_global_helper(*args, **kwargs)


class LazyStrictSavingGlobalHelperRunner(
    GlobalHelperMixin,
    LazyStrictSavingRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания классов ранеров с отложенным сохранением объектов в строгом режиме c
    глобальным помощником.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._global_helper: BaseRunnerHelper = self._prepare_global_helper(*args, **kwargs)


class LazySavingSettableQueueRunner(
    BaseRunner,
    LazySavingRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания ранеров с устанавливаемой очередью на сохранение.
    """

    def __init__(
        self,
        *args,
        queue_to_save: Optional[Deque] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # очередь содержащая объекты на сохранение
        self._queue_to_save: Optional[Deque] = queue_to_save

    def set_queue(self, queue_to_save):
        """
        Установка очереди на сохранение
        """
        self._queue_to_save = queue_to_save

    def _prepare_runnable_before_enqueue(
        self,
        runnable: Union['LazySavingSettableQueueRunner', LazyDelegateSavingSettableQueueFunction],
    ):
        runnable.set_queue_to_save(
            queue_to_save=self._queue_to_save,
        )


class LazyDelegateSavingSettableQueueRunner(
    LazySavingSettableQueueRunner,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания ранеров с устанавливаемой очередью на сохранение. Используется в связке с
    LazySavingGeneralQueueRunner в качестве пусковкика. В качестве запускаемых объектов используются
    LazyDelegateSavingSettableQueueFunction и его потомки, и объекты самого класса и его потомков.
    """

    def do_save(self, *args, **kwargs):
        """
        Сохранение делегировано ранеру.
        """


class LazySavingGeneralQueueRunner(
    BaseRunner,
    LazySavingActionModelRunnableObject,
    metaclass=ABCMeta,
):
    """
    Абстрактный класс для создания ранеров с единой очередью сохранения для всех исполняемых объектов. Используется в
    паре LazyDelegateSavingSettableQueueFunction, LazyDelegateSavingSettableQueueRunner и их наследниками.
    """

    def _prepare_runnable_before_enqueue(
        self,
        runnable: Union['LazyDelegateSavingSettableQueueRunner', LazyDelegateSavingSettableQueueFunction],  # noqa
    ):
        runnable.set_queue_to_save(
            queue_to_save=self._queue_to_save,
        )
