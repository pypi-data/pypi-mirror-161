from abc import (
    ABCMeta,
    abstractmethod,
)

from function_tools.results import (
    BaseRunnableResult,
)


class ResultPresenter(metaclass=ABCMeta):
    """
    Презентер результата выполнения запускаемого объекта.
    """
    def __init__(self, runnable_result: BaseRunnableResult):
        self._runnable_result = runnable_result

        self._presentable_result = None

    @abstractmethod
    def represent(self):
        """
        Осуществляется преобразование результата выполнения запускаемого
        объекта в нужный вид
        """



