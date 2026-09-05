class TableNotFoundError(Exception):
    """Вызывается, когда в PDF не найдена таблица."""
    pass

class InvalidArgumentError(Exception):
    """Вызывается, когда маржа меньше 0."""
    pass

class FileNotFoundError(Exception):
    """Вызывается когда файл не найден"""
    pass