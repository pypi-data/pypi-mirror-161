import warnings

from function_tools.strategies import (
    FunctionImplementationStrategy,
    SyncBaseRunnerBaseFunctionImplementationStrategy,
    SyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy,
    SyncLazySavingRunnerLazyDelegateSavingPredefinedQueueFunctionImplementationStrategy,
)


warnings.warn(
    message=(
        'Модуль function_tools.management.strategies был перемещен function_tools.strategies. Просьба внести '
        'исправления в импорты.'
    ),
    category=DeprecationWarning,
    stacklevel=2,
)
