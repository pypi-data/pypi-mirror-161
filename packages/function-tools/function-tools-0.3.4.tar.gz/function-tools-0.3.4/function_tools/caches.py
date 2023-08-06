from collections import (
    Iterable,
    OrderedDict,
    Sequence,
)
from copy import (
    deepcopy,
)
from datetime import (
    date,
)
from operator import (
    attrgetter,
)
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

from django.db.models import (
    Model,
)

from function_tools.enums import (
    TransferPeriodEnum,
)
from function_tools.strings import (
    DATE_FROM_MORE_OR_EQUAL_DATE_TO_ERROR,
    SEARCHING_KEY_SIZE_LESS_THAN_DEFAULT_SEARCHING_KEY_ERROR,
    SEARCHING_KEY_SIZE_MORE_THAN_DEFAULT_SEARCHING_KEY_ERROR,
)
from function_tools.types import (
    QueryType,
)
from function_tools.utils import (
    date2str,
    deep_getattr,
)


class BaseCache:
    """
    Кеш-заглушка
    """

    def __init__(self, *args, **kwargs):
        super().__init__()


class EntityCache(BaseCache):
    """
    Базовый класс кеша объектов сущности
    """

    def __init__(
        self,
        model: Type[Model],
        *args,
        select_related_fields: Optional[Tuple[str, ...]] = None,
        only_fields: Optional[Tuple[str, ...]] = None,
        additional_filter_params: Optional[Dict[str, Any]] = None,
        searching_key: Union[str, Tuple[str, ...]] = ('pk', ),
        **kwargs,

    ):
        super().__init__(*args, **kwargs)

        self._model = model
        self._select_related_fields = select_related_fields
        self._only_fields = only_fields
        self._actual_entities_queryset = self._prepare_actual_entities_queryset()  # noqa

        self._searching_key = (
            searching_key if (
                isinstance(searching_key, Iterable) and
                not isinstance(searching_key, str)
            ) else
            (searching_key, )
        )

        self._additional_filter_params = additional_filter_params or {}

        self._entities = None
        self._entities_hash_table = None

        self._before_prepare()
        self._prepare()
        self._after_prepare()

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} @model="{self._model.__name__}" '
            f'@searching_key="{self._searching_key}">'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def entities(self) -> Union[QueryType[Model], List[Model]]:
        """
        Возвращает список объектов либо QuerySet в зависимости от подхода к
        получению объектов
        """
        return self._entities

    def _before_prepare(self):
        """
        Точка расширения перед подготовкой кеша
        """
        pass

    def _after_prepare(self):
        """
        Точка расширения после подготовки кеша
        """
        pass

    def _prepare(self):
        """
        Метод подготовки кеша
        """
        self._prepare_entities()
        self._prepare_entities_hash_table()

    def _prepare_entities(self):
        """
        Получение выборки объектов модели по указанными параметрам
        """
        self._entities = self._actual_entities_queryset.filter(
            **self._additional_filter_params,
        )

        if self._only_fields:
            self._entities = self._entities.only(*self._only_fields)

        self._entities = self._entities.distinct()

    def _prepare_entities_hash_table(self):
        """
        Отвечает за построение хеш таблицы для дальнейшего поиска. В качестве
        ключа можно задавать строку - наименование поля или кортеж наименований
        полей.

        Если требуется доступ через внешний ключ, то необходимо использовать
        точку в качестве разделителей. Например,
        searching_key = tuple('account_id', 'supplier.code')
        """
        hash_table = {}

        key_items_count = len(self._searching_key)
        for entity in self._entities:
            temp_hash_item = hash_table

            for index, key_item in enumerate(self._searching_key, start=1):
                key_item_value = deep_getattr(entity, key_item)

                if key_item_value is not None:
                    if index == key_items_count:
                        if key_item_value not in temp_hash_item:
                            temp_hash_item[key_item_value] = entity
                        else:
                            if isinstance(temp_hash_item[key_item_value], set):
                                temp_hash_item[key_item_value].add(
                                    entity
                                )
                            else:
                                temp_hash_item[key_item_value] = {
                                    temp_hash_item[key_item_value], entity
                                }
                    else:
                        if key_item_value not in temp_hash_item:
                            temp_hash_item[key_item_value] = {}

                        temp_hash_item = temp_hash_item[key_item_value]
                else:
                    break

        self._entities_hash_table = hash_table

    def _prepare_actual_entities_queryset(self):
        """
        Подготовка менеджера с указанием идентификатора учреждения и состояния,
        если такие имеются у модели
        """
        actual_entities_queryset = self._model._base_manager.all()

        if self._select_related_fields:
            actual_entities_queryset = actual_entities_queryset.select_related(
                *self._select_related_fields,
            )

        return actual_entities_queryset

    def filter(
        self,
        only_first: bool = False,
        **kwargs,
    ):
        """
        Метод фильтрации объектов кеша по заданным параметрам.

        Пример использования:

        some_objects_list = cache.filter(code='12345', only_first=True)

        Можно получать первое попавшееся значение с указанием only_first=True
        """
        filter_ = OrderedDict()
        for field_name, field_value in kwargs.items():
            prepared_field_name = field_name.split('__in')[0]
            prepared_field_value = (
                set(field_value) if
                self._check_is_iterable(field_value) else
                {field_value}
            )
            filter_[prepared_field_name] = prepared_field_value

        result = list(
            filter(
                lambda entity: all(
                    [
                        getattr(entity, field_name) in filter_[field_name]
                        for field_name in filter_.keys()
                    ]
                ),
                self._entities
            )
        )

        if only_first:
            if result:
                result = result[0]
            else:
                result = None

        return result

    def flat_values_list(
        self,
        field_name: str,
    ):
        """
        Получение плоского списка значений объектов указанного свойства без
        пустых значений.

        : param field_name: наименование поля
        """
        return list(
            filter(
                None,
                [
                    getattr(entity, field_name, None)
                    for entity in self._entities
                ]
            )
        )

    def _check_is_iterable(self, object_):
        """
        Проверяет, является ли передаваемый объект итерабельным
        """
        return (
            isinstance(object_, (Iterable, Sequence)) and
            not isinstance(object_, str)
        )

    def get_by_key(
        self,
        key: Union[Any, Tuple[Any]],
        strict_mode=True,
    ):
        """
        Метод получения значения из кеша по ключу поиска.

        В общем случае передаваемый ключ должен совпадать с _searching_key.
        Если отключить строгий режим поиска - strict_mode=False, то можно
        получить промежуточный результат по части ключа следующего с начала.
        """
        key = (
            key if
            self._check_is_iterable(key) else
            (key, )
        )
        key_items_count = len(key)
        searching_key_items_count = len(self._searching_key)

        if key_items_count > searching_key_items_count:
            raise ValueError(
                SEARCHING_KEY_SIZE_MORE_THAN_DEFAULT_SEARCHING_KEY_ERROR
            )
        elif key_items_count < searching_key_items_count and strict_mode:
            raise ValueError(
                SEARCHING_KEY_SIZE_LESS_THAN_DEFAULT_SEARCHING_KEY_ERROR
            )

        result = None
        temp_hash_item = self._entities_hash_table
        for index, key_item in enumerate(key, start=1):
            if key_item not in temp_hash_item:
                if not strict_mode and index != 1:
                    result = temp_hash_item

                break

            temp_hash_item = temp_hash_item[key_item]

            if index == key_items_count:
                result = temp_hash_item

        return result

    def values_list(
        self,
        fields: Tuple[str, ...],
    ) -> Optional[List[Tuple]]:
        """
        Получение списка кортежей состоящих из значений полей объектов согласно
        заданным параметрам

        :param fields: кортеж наименований полей
        """
        fields_getter = attrgetter(*fields)

        return [
            fields_getter(entity)
            for entity in self._entities
        ]

    def first(self):
        """
        Получение первого элемента из кеша
        """
        result = None

        if self._entities:
            result = self._entities[0]

        return result


class ActualEntityCache(EntityCache):
    """
    Базовый класс кеша актуальных записей сущности
    """

    def __init__(
        self,
        actual_date,
        *args,
        **kwargs,
    ):
        self._actual_date = actual_date

        super().__init__(*args, **kwargs)

    def _prepare_actual_entities_queryset(self) -> Dict[str, date]:
        """
        Метод получения фильтра актуализации по дате.
        """
        actual_entities_queryset = super()._prepare_actual_entities_queryset()

        actual_entities_queryset = actual_entities_queryset.filter(
            begin__lte=self._actual_date,
            end__gte=self._actual_date,
        )

        return actual_entities_queryset


class PeriodicalEntityCache(BaseCache):
    """
    Базовый класс периодического кеша.

    Кеш создается для определенной модели с указанием двух дат, на которые
    должны быть собраны кеши актуальных объектов модели.

    Для примера, может использоваться при переносах остатков на очередной год
    с 31 декабря на 1 января нового года.
    """

    entity_cache_class = EntityCache

    def __init__(
        self,
        date_from: date,
        date_to: date,
        model: Type[Model],
        *args,
        select_related_fields: Optional[Tuple[str, ...]] = None,
        only_fields: Optional[Tuple[str, ...]] = None,
        additional_filter_params: Optional[Dict[str, Any]] = None,
        searching_key: Union[str, Tuple[str, ...]] = ('pk', ),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if date_from >= date_to:
            raise ValueError(
                DATE_FROM_MORE_OR_EQUAL_DATE_TO_ERROR
            )

        self._model = model
        self._select_related_fields = select_related_fields
        self._only_fields = only_fields

        self._additional_filter_params = additional_filter_params or {}
        self._searching_key = searching_key

        self._date_from = date_from
        self._date_to = date_to

        self._old_entities_cache: Optional[EntityCache] = None
        self._new_entities_cache: Optional[EntityCache] = None

        self._before_prepare()
        self._prepare()
        self._after_prepare()

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} @model="{self._model.__name__}" '
            f'@date_from="{date2str(self._date_from)}" '
            f'@date_to="{date2str(self._date_to)}" '
            f'@searching_key="{self._searching_key}">'
        )

    def __str__(self):
        return self.__repr__()

    @property
    def old(self):
        """
        Кеш объектов модели актуальных на начальную дату
        """
        return self._old_entities_cache

    @property
    def new(self):
        """
        Кеш объектов модели актуальный на конечную дату
        """
        return self._new_entities_cache

    def _get_actuality_filter(
        self,
        period_type: str,
    ) -> Dict[str, date]:
        """
        Метод получения фильтра актуализации по дате.

        При получении счетов или аналитик при переносе остатков необходимо
        учитывать период действия следуя следующей логике:
        -- старые - begin < date_from &&  end >= date_from
        -- новые - begin <= date_to && end > date_to

        :param dict period_type: словарь с параметрами для актуализации по дате
        :return:
        """
        if period_type == TransferPeriodEnum.OLD:
            actuality_filter = {
                'begin__lt': self._date_from,
                'end__gte': self._date_from,
            }
        else:
            actuality_filter = {
                'begin__lte': self._date_to,
                'end__gt': self._date_to,
            }

        return actuality_filter

    def _prepare_entities_cache(
        self,
        additional_filter_params: Optional[Dict[str, Any]]
    ):
        """
        Создание кеша объектов модели на указанную дату по указанным параметром
        с ключом поиска для построения хеш-таблицы
        """
        entities_cache = self.entity_cache_class(
            model=self._model,
            select_related_fields=self._select_related_fields,
            only_fields=self._only_fields,
            additional_filter_params=additional_filter_params,
            searching_key=self._searching_key,
        )

        return entities_cache

    def _prepare_additional_filter_params(
        self,
        period_type: str,
    ):
        """
        Подготовка словаря с дополнительными параметрами для дальнейшей
        фильтрации объектов при формировании кеша
        """
        additional_filter_params = deepcopy(self._additional_filter_params)
        additional_filter_params.update(
            **self._get_actuality_filter(
                period_type=period_type,
            )
        )

        return additional_filter_params

    def _prepare_old_additional_filter_params(self):
        """
        Подготовка дополнительных параметров фильтрации на начальную дату
        """
        return self._prepare_additional_filter_params(
            period_type=TransferPeriodEnum.OLD,
        )

    def _prepare_new_additional_filter_params(self):
        """
        Подготовка дополнительных параметров фильтрации на конечную дату
        """
        return self._prepare_additional_filter_params(
            period_type=TransferPeriodEnum.NEW,
        )

    def _prepare_old_entities_cache(self):
        """
        Формирование кеша объектов модели на начальную дату
        """
        additional_filter_params = self._prepare_old_additional_filter_params()
        self._old_entities_cache = self._prepare_entities_cache(
            additional_filter_params=additional_filter_params,
        )

    def _prepare_new_entities_cache(self):
        """
        Формирование кеша объектов модели на конечную дату
        """
        additional_filter_params = self._prepare_new_additional_filter_params()
        self._new_entities_cache = self._prepare_entities_cache(
            additional_filter_params=additional_filter_params,
        )

    def _before_prepare(self):
        """
        Точка расширения перед формированием кеша
        """

    def _prepare(self):
        """
        Формирование кешей на начальную и конечную даты
        """
        self._prepare_old_entities_cache()
        self._prepare_new_entities_cache()

    def _after_prepare(self):
        """
        Точка расширения после формирования кеша
        """


class CacheStorage(BaseCache):
    """
    Хранилище кешей.

    Для выполнения функций, в большинстве случаев, необходимы кеши для
    множества сущностей созданные по особым правилам, но подчиняющиеся общим.
    Для их объединения и применения в функции создаются хранилища, содержащие кеши в виде публичных свойств, с
    которыми в дальнейшем удобно работать
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PatchedGlobalCacheStorage(CacheStorage):
    """
    Хранилище кешей с функциональностью патчинга кеша или хранилища кешей с использованием глобального (внешнего)
    кеша или хранилища кешей. Пригождается в случае использования глобального хелпера, когда есть необходимость
    создания кеша функции на основе кеша ранера.
    """

    def patch_by_global_cache(
        self,
        global_cache: BaseCache,
    ):
        """
        Патчинг кеша или хранилища кеша с использованием внешнего кеша или хранилища кешей.

        Args:
            global_cache: Внешний кеш или хранилище кешей.
        """
        pass
