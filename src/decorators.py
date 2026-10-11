import functools


def log(filename=None):
    """
    Декоратор для логирования вызовов функций.

    Args:
        filename: Необязательный путь к файлу для записи логов.
                  Если не указан, логи выводятся в консоль.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                message = f"{func.__name__} ok"
            except Exception as e:
                message = (
                    f"{func.__name__} error: {type(e).__name__}. "
                    f"Inputs: {args}, {kwargs}"
                )
                result = None
                raise
            finally:
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(message + "\n")
                else:
                    print(message)
            return result

        return wrapper

    return decorator
