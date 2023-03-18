import traceback

from polywit.exceptions.exceptions import ValidationError


def validation_error_handler(exception: ValidationError):
    """
    Catches all thrown errors from a given function and reraises a custom polywit error
    :param exception: Type of exception to be rethrown and caught in the main entrypoint
    """
    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                raise exception from exc
            return result
        return wrapper

    return outer_wrapper
