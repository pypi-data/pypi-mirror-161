import sys
from typing import (
    Dict,
    List,
    Optional,
    Type,
    Union,
)

from django.core.management import (
    color_style,
)
from django.core.management.base import (
    BaseCommand,
)
from django.db import (
    transaction,
)

from function_tools.models import (
    Entity,
    EntityType,
)
from function_tools.storages import (
    EntityStorage,
)
from function_tools.management.strategies import SyncBaseRunnerBaseFunctionImplementationStrategy


class EntityRegistrar:
    """
    Регистратор классов сущностей системы.
    """

    compared_fields = {
        'class_name': '__name__',
        'verbose_name': 'verbose_name',
        'tags': 'tags',
    }

    def __init__(self, logger):
        self._logger = logger

        self._entities: Optional[Dict[str, Dict[str, Union[Type[object], str]]]] = None

        self._registered_entities: Optional[List[Entity]] = None
        self._registered_entities_map: Optional[Dict[str, Entity]] = None

        self._style = color_style()

        self._prepare_registered_entities()
        self._prepare_entities()

    def _prepare_registered_entities(self):
        """
        Подготовка зарегистрированных сущностей в базе данных.
        """
        self._registered_entities = list(Entity.objects.all())

        self._registered_entities_map = {
            str(registered_entity.uuid): registered_entity
            for registered_entity in self._registered_entities
        }

    def _prepare_entities(self):
        """
        Поиск реализованных классов сущностей.
        """
        entity_storage = EntityStorage()
        entity_storage.prepare()

        self._entities = entity_storage.flat_entities

    def _process_creating_entities(self):
        """
        Обработка создаваемых классов сущностей.
        """
        self._logger.write('start processing creating entities..\n')

        for_creating = []

        creating_entity_uuids = filter(
            lambda uuid: uuid not in self._registered_entities_map.keys(),
            self._entities.keys()
        )

        for creating_entity_uuid in creating_entity_uuids:
            entity = self._entities[creating_entity_uuid]

            for_creating.append(
                Entity(
                    uuid=creating_entity_uuid,
                    verbose_name=entity['class'].verbose_name,
                    tags=entity['class'].tags,
                    type_id=EntityType.get_type(entity['class']).key,
                    class_name=entity['class'].__name__,
                    import_path=entity['import_path'],
                )
            )

        if for_creating:
            Entity.objects.bulk_create(objs=for_creating)

        self._logger.write('finished processing creating entities.\n')

    def _compare_entities(
        self,
        registered_entity: Entity,
        runtime_entity: Type[object],
        runtime_entity_import_path: str,
    ) -> List[str]:
        """
        Производит сравнение значений полей двух экземпляров сущности из базы и из кода. Возвращает список полей для
        обновления.
        """
        updated_fields = []

        for model_field_name, class_field_name in self.compared_fields.items():
            if getattr(registered_entity, model_field_name) != getattr(runtime_entity, class_field_name):
                updated_fields.append(model_field_name)

        if registered_entity.import_path != runtime_entity_import_path:
            updated_fields.append('import_path')

        return updated_fields

    def _process_updating_entities(self):
        """
        Обработка обновляемых классов сущностей.
        """
        self._logger.write('start processing updating entities..\n')

        updating_entities_uuids = filter(
            lambda uuid: uuid in self._registered_entities_map,
            self._entities.keys()
        )

        for updating_entity_uuid in updating_entities_uuids:
            updated_fields = self._compare_entities(
                registered_entity=self._registered_entities_map[updating_entity_uuid],
                runtime_entity=self._entities[updating_entity_uuid]['class'],
                runtime_entity_import_path=self._entities[updating_entity_uuid]['import_path'],
            )

            if updated_fields:
                for updated_field in updated_fields:
                    if updated_field == 'import_path':
                        self._registered_entities_map[updating_entity_uuid].import_path = (
                            self._entities[updating_entity_uuid]['import_path']
                        )
                    else:
                        setattr(
                            self._registered_entities_map[updating_entity_uuid],
                            updated_field,
                            getattr(self._entities[updating_entity_uuid]['class'], self.compared_fields[updated_field])
                        )

                    # Иду на преступный шаг с генерацией некоторого количества запросов в БД, все только для того, чтобы
                    # изменить дату и время обновления записи
                    self._registered_entities_map[updating_entity_uuid].save()

        self._logger.write('processing updating entities finished.\n')

    def _process_deleting_entities(self):
        """
        Обработка удаленных, перенесенных или находящихся в отключенных плагинах сущностях системы.
        """
        self._logger.write('start processing deleting entities..\n')

        deleted_entities_uuids = set(
            self._registered_entities_map.keys()
        ).difference(self._entities.keys())

        if deleted_entities_uuids:
            for deleted_entity_uuid in deleted_entities_uuids:
                sys.stdout.write(
                    self._style.NOTICE(
                        f'Found registered Entity in the database, but not found implementation. Entity with UUID "'
                        f'{deleted_entity_uuid}". Please, check it!\n'
                    )
                )

        self._logger.write('end processing deleting entities..\n')

    def _register(self):
        """
        Регистрация реализованных сущностей системы.
        """
        self._process_creating_entities()
        self._process_updating_entities()
        self._process_deleting_entities()

    def run(self):
        self._logger.write('start function_tools entities registration..\n')

        self._register()

        self._logger.write('function_tools entities registration finished.\n')


class Command(BaseCommand):
    """
    Команда регистрации сущностей системы.
    """

    help = 'Команда предназначена для регистрации сущностей системы, реализованных при помощи function-tools.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        registrar = EntityRegistrar(logger=self.stdout)
        registrar.run()
