from inspect import (
    isclass,
)
from pathlib import (
    Path,
)
from typing import (
    Optional,
    Type,
    Union,
)

from django.contrib.postgres.fields import (
    ArrayField,
)
from django.db.models import (
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    UUIDField,
)

from function_tools.functions import (
    BaseFunction,
)
from function_tools.managers import (
    RunnerManager,
)
from function_tools.runners import (
    BaseRunner,
)
from function_tools.strategies import (
    FunctionImplementationStrategy,
)
from m3_db_utils.models import (
    ModelEnumValue,
    TitledModelEnum,
)


class ImplementationStrategy(TitledModelEnum):
    """
    Перечисление стратегий реализации функций.
    """

    class Meta:
        db_table = 'function_tools_implementation_strategy'
        verbose_name = 'Стратегия создания функции'
        extensible = True


class EntityType(TitledModelEnum):
    """
    Тип сущности function_tools.
    """

    MANAGER = ModelEnumValue(
        title='Менеджер',
        module='managers',
        base_class=RunnerManager,
    )

    RUNNER = ModelEnumValue(
        title='Ранер',
        module='runners',
        base_class=BaseRunner,
    )

    FUNCTION = ModelEnumValue(
        title='Функция',
        module='functions',
        base_class=BaseFunction,
    )

    STRATEGY = ModelEnumValue(
        title='Стратегия создания Функции',
        module='strategies',
        base_class=FunctionImplementationStrategy,
    )

    class Meta:
        db_table = 'function_tools_entity_type'
        verbose_name = 'Тип сущности'
        verbose_name_plural = 'Типы сущностей'

    @classmethod
    def get_type(
        cls,
        entity: Union[object, Type[object]],
    ) -> Optional[ModelEnumValue]:
        """
        Определение типа сущности. Может передаваться как класс, так и экземпляр класса.

        Args:
            entity: Класс или экземпляр класса
        """
        entity_type = None

        if isclass(entity):
            check_method = issubclass
        else:
            check_method = isinstance

        for temp_entity_type in cls.get_model_enum_values():
            if check_method(entity, temp_entity_type.base_class):
                entity_type = temp_entity_type
                break

        return entity_type

    @classmethod
    def get_type_by_path(cls, module_path: Union[str, Path]):
        """
        Определение типа сущности по пути модуля.

        Args:
            module_path: Путь модуля
        """
        module_path = Path(module_path)

        module_name = module_path.name.split('.')[0]

        entity_type = None

        for temp_entity_type in cls.get_model_enum_values():
            if temp_entity_type.module == module_name:
                entity_type = temp_entity_type
                break

        return entity_type


class Entity(Model):
    """
    Сущность function_tools хранящаяся в базе данных.
    """

    uuid = UUIDField(
        verbose_name='Уникальный идентификатор',
        primary_key=True,
        unique=True,
    )

    class_name = CharField(
        verbose_name='Название класса',
        max_length=256,
    )

    import_path = CharField(
        verbose_name='Путь до модуля для импорта',
        max_length=512,
    )

    verbose_name = CharField(
        verbose_name='Человеко читаемое название',
        max_length=512,
        default='Имя сущности не определено',
    )

    tags = ArrayField(
        base_field=CharField(max_length=128, blank=True),
        default=list,
    )

    type = ForeignKey(
        to=EntityType,
        verbose_name='Тип сущности',
    )

    created_at = DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True,
    )
    updated_at = DateTimeField(
        verbose_name='Дата и время обновления',
        auto_now=True,
    )

    class Meta:
        db_table = 'function_tools_entity'
        verbose_name = 'Сущность'
        verbose_name_plural = 'Сущности'
