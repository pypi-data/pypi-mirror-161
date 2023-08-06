from sys import (
    stdout,
)


def function_tools_after_migrate_receiver(sender, **kwargs):
    """
    Действия выполняемые после прогона миграций.
    """
    from function_tools.management.commands.register_entities import (
        EntityRegistrar,
    )

    registrar = EntityRegistrar(logger=stdout)
    registrar.run()
