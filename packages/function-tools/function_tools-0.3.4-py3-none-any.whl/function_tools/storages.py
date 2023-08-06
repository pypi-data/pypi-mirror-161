import sys
from collections import (
    defaultdict,
)
from importlib import (
    import_module,
)
from inspect import (
    isclass,
)
from pathlib import (
    Path,
)
from types import (
    ModuleType,
)
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from django.apps import (
    AppConfig,
)
from django.conf import (
    settings,
)

from function_tools.functions import (
    BaseFunction,
)
from function_tools.managers import (
    RunnerManager,
)
from function_tools.models import (
    EntityType,
)
from function_tools.runners import (
    BaseRunner,
)
from m3_db_utils.models import (
    ModelEnumValue,
)


if TYPE_CHECKING:
    from django.apps import (
        AppConfig,
    )


class EntityStorage:
    """
    Хранилище классов сущностей реализованных в системе.

    Собираются только те сущности, типы которых указаны в модели-перечислении
    function_tools.models.function_tools.models.EntityType.
    """

    def __init__(self):
        # Словарь для хранения найденных классов реализованных сущностей
        self._entities = {
            model_enum_value.key: defaultdict()
            for model_enum_value in EntityType.get_model_enum_values()
        }

        self._checked_application_paths: List[Path] = []

        self._entity_module_patterns: List[str] = [
            f'**/**/{model_enum_value.module}.py'
            for model_enum_value in EntityType.get_model_enum_values()
        ]

        self._entities_modules: List[Tuple[Path, str, ModuleType]] = []

        self._sys_path = set(sys.path)

    @property
    def entities(self) -> Dict[str, Dict[str, Dict[str, Union[str, Type[object]]]]]:
        """
        Все классы сущностей реализованных в системе, сгруппированные по типу сущностям.
        """
        return self._entities

    @property
    def flat_entities(self) -> Dict[str, Dict[str, Union[Type[object], str]]]:
        """
        Возвращает плоский словарь с классами сущностей с UUID в качестве ключа.
        """
        flat_entities = {}

        for entities in self._entities.values():
            flat_entities.update(entities)

        return flat_entities

    def _get_module_import_path(self, module_path: str) -> str:
        """
        Предназначен для получения пути пакета для импорта класса сущности.

        Args:
            module_path: абсолютный путь до модуля
        """
        package_path = max(
            filter(
                lambda path: path in module_path,
                self._sys_path
            )
        )

        relative_module_path = module_path.split(f'{package_path}/')[1]
        import_path = '.'.join(relative_module_path.split('.')[0].split('/'))

        return import_path

    def _get_application_path(self, application_name: Union[str, 'AppConfig']) -> Optional[Path]:
        """
        Получение пути приложения.

        Args:
            application_name: Наименование приложения
        """
        # TODO EDUSCHL-17934 В app_name могут прилетать AppConfig. Необходимо произвести доработку и обработать
        #  такие случаи.
        try:
            app_module = import_module(application_name)
        except ModuleNotFoundError:
            return

        application_path = Path(app_module.__path__[0])

        # Если поиск уже осуществлялся по родительской директории,
        # то проверку нужно пропустить
        is_already_checked = False

        for checked_application_path in self._checked_application_paths:
            try:
                is_already_checked = application_path.is_relative_to(Path(checked_application_path))
            # В CI падает с ошибкой 'PosixPath' object has no attribute 'is_relative_to', хотя локально не
            # воспроизводится
            except AttributeError:
                continue

            if is_already_checked:
                break

        return application_path if not is_already_checked else None

    def _find_application_entities_modules(self, application_name: Union[str, 'AppConfig']):
        """
        Поиск модулей зарегистрированных типов сущностей в приложении.

        Args:
            application_name: имя приложения
        """
        application_path = self._get_application_path(application_name=application_name)

        if application_path:
            for entity_module_pattern in self._entity_module_patterns:
                entity_module_paths = application_path.glob(entity_module_pattern)

                for entity_module_path in entity_module_paths:
                    entity_module_path = str(entity_module_path)

                    import_path = self._get_module_import_path(
                        module_path=entity_module_path,
                    )

                    try:
                        import_module(import_path)

                        entity_module = sys.modules[import_path]
                    except (KeyError, RuntimeError):
                        continue

                    self._entities_modules.append((Path(entity_module_path), import_path, entity_module))

            self._checked_application_paths.append(application_path)

    def _find_entities_modules(self):
        """
        Поиск модулей зарегистрированных типов сущностей.
        """
        for application_name in settings.INSTALLED_APPS:
            self._find_application_entities_modules(application_name=application_name)

    def _prepare_entities(self):
        """
        Поиск фабрик во всех подключенных приложениях.
        """
        processed_paths = list()

        for entity_module_path, entity_module_import_path, entity_module in self._entities_modules:
            if entity_module_path in processed_paths:
                continue
            else:
                processed_paths.append(entity_module_path)

            entity_type: ModelEnumValue = EntityType.get_type_by_path(module_path=entity_module_path)

            for item_name, item in entity_module.__dict__.items():
                if (
                    isclass(item)
                    and issubclass(item, entity_type.base_class)
                    and hasattr(item, 'uuid')
                    and item.uuid
                ):
                    if item.uuid in self.flat_entities.keys() and item != self.flat_entities[item.uuid]['class']:
                        raise RuntimeError(f'Found duplicated UUID {item.uuid}! Please check and change it!')

                    self._entities[entity_type.key][item.uuid] = {
                        'class': item,
                        'import_path': entity_module_import_path,
                    }

    def prepare_runner_function_map(
        self,
        runner_class: Type[BaseRunner],
        runner_tags: Optional[Set[str]] = None,
        function_tags: Optional[Set[str]] = None,
    ) -> Tuple[Type[BaseRunner], List]:
        """
        Собирает и возвращает список функций запускаемых в рамках работы менеджера.
        """
        entities = []

        for runnable_class in runner_class._prepare_runnable_classes():
            if issubclass(runnable_class, BaseRunner):
                if runner_tags:
                    if not runner_tags.difference(runnable_class.tags):
                        entities.append(
                            self.prepare_runner_function_map(
                                runner_class=runnable_class,
                            )
                        )
                else:
                    entities.append(
                        self.prepare_runner_function_map(
                            runner_class=runnable_class,
                        )
                    )

                continue
            elif issubclass(runnable_class, BaseFunction):
                if function_tags:
                    if not function_tags.difference(runnable_class.tags):
                        entities.append(runnable_class)
                else:
                    entities.append(runnable_class)

        return runner_class, entities

    def prepare_manager_runnable_map(
        self,
        manager_tags: Optional[Set[str]] = None,
        runner_tags: Optional[Set[str]] = None,
        function_tags: Optional[Set[str]] = None,
    ) -> Dict[Type[RunnerManager], Tuple[Type[BaseRunner], List]]:
        """
        Строит карту соответствия менеджер -> ранер -> функция.

        Args:
            manager_tags: теги менеджеров;
            runner_tags: теги ранеров;
            function_tags: теги функций.
        """
        manager_runner_function_map = dict()

        manager_classes: List[Type[RunnerManager]] = []
        for entity in self.entities[EntityType.MANAGER.key].values():
            if manager_tags:
                if not manager_tags.difference(entity['class'].tags):
                    manager_classes.append(entity['class'])
            else:
                manager_classes.append(entity['class'])

        for manager_class in manager_classes:
            runner_class = manager_class.runner_class

            manager_runner_function_map[manager_class] = self.prepare_runner_function_map(
                runner_class=runner_class,
                runner_tags=runner_tags,
                function_tags=function_tags,
            )

        return manager_runner_function_map

    def _find_functions(self, entities, function_uuids):
        """
        Поиск функций в списке сущностей, который может содержать вложенный список.
        """
        for entity in entities:
            if isinstance(entity, tuple):
                _, temp_entities = entity

                self._find_functions(
                    entities=temp_entities,
                    function_uuids=function_uuids,
                )
            elif issubclass(entity, BaseFunction):
                function_uuids.append(entity.uuid)

    def prepare_manager_function_uuid_map(
        self,
        manager_tags: Optional[Set[str]] = None,
        runner_tags: Optional[Set[str]] = None,
        function_tags: Optional[Set[str]] = None,
    ) -> Dict[str, List[str]]:
        """
        Возвращает карту соответствия менеджера и функций.

        В качестве ключей и значений списка используются UUID-ы сущностей.
        """
        manager_function_uuid_map = {}

        manager_runnable_map = self.prepare_manager_runnable_map(
            manager_tags=manager_tags,
            runner_tags=runner_tags,
            function_tags=function_tags,
        )

        for manager_class, (_, entities) in manager_runnable_map.items():
            function_uuids = []

            self._find_functions(
                entities=entities,
                function_uuids=function_uuids,
            )

            manager_function_uuid_map[manager_class.uuid] = function_uuids

        return manager_function_uuid_map

    def prepare(self):
        """
        Подготовка хранилища. Производится его наполнение реализованными классами сущностей.
        """
        self._find_entities_modules()
        self._prepare_entities()
