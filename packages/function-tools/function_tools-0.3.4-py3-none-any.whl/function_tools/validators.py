class BaseValidator:
    """
    Базовый класс для создания валидатора
    """

    def __init__(self, *args, **kwargs):
        super().__init__()

    def validate(self, runnable):
        """
        Точка входа работы валидатора.

        Результат валидации должен быть записан в runnable.result
        """
