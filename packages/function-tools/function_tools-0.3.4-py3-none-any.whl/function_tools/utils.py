import operator

from django.conf import (
    settings,
)
from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.db.models import (
    Model,
)
from django.utils import (
    datetime_safe,
)


def deep_getattr(
    obj,
    attr,
    default=None,
):
    """
    Получить значение атрибута с любого уровня цепочки вложенных объектов.

    :param object obj: объект, у которого ищется значение атрибута
    :param str attr: атрибут, значение которого необходимо получить (
        указывается полная цепочка, т.е. 'attr1.attr2.atr3')
    :param object default: значение по умолчанию
    :return: значение указанного атрибута или значение по умолчанию, если
        атрибут не был найден
    """
    try:
        value = operator.attrgetter(attr)(obj)
    except (
        AttributeError,
        ValueError,
        ObjectDoesNotExist,
    ):
        value = default

    return value


def date2str(date, template=None):
    """
    datetime.strftime глючит с годом < 1900
    типа обходной маневр (взято из django)

    WARNING from django:
    # This library does not support strftime's \"%s\" or \"%y\" format strings.
    # Allowed if there's an even number of \"%\"s because they are escaped.
    """
    return datetime_safe.new_datetime(date).strftime(
        template or
        settings.DATE_FORMAT or
        '%d.%m.%Y'
    )


def rebind_model_rel_id(obj):
    """
    Функция установки идентификатора объекта выступающего в роли внешней связи. Для FK-полей, если сохранили внешнюю
    модель, то проставим значение id в поле.

    Args:
        obj: объект, у которого должно быть произведено проставление идентификаторов объектов внешних связей
    """
    assert isinstance(obj, Model)

    for field in obj._meta.concrete_fields:
        if (
            field.is_relation
            and not getattr(obj, field.attname, None)
            and deep_getattr(obj, f'{field.name}.pk')
        ):
            # Получение объекта-значения внешнего ключа
            saved_obj = getattr(obj,  field.name)

            # Установка идентификатора объекта-значения внешнего ключа
            setattr(obj, field.attname, deep_getattr(obj, f'{field.name}.pk'))

            # Повторная установка объекта-значения внешнего ключа, т.к. при установке идентификатора, могла быть
            # произведена замена объекта. Такое поведение было замечено для моделей с выстроенной иерархией наследования
            setattr(obj, field.name, saved_obj)
