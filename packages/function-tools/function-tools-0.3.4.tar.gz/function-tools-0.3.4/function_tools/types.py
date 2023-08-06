from typing import (
    Generic,
    Iterator,
    TypeVar,
)

from django.db.models import (
    QuerySet,
)

_Z = TypeVar("_Z")


class QueryType(Generic[_Z], QuerySet):
    """
    Используется при типизировании QuerySet для того, чтобы интерпритатор
    понимал, с каким объектами нужно работать при итерировании

    Пример использования:
    acc_analytics: QueryType[AccountAnalytic] = AccountAnalytic.objects.filter(...
    """

    def __iter__(self) -> Iterator[_Z]: ...
