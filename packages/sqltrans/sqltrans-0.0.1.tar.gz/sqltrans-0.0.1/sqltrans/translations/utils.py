from functools import wraps


def register_rule(rules_repository):
    def decorator(func):
        rules_repository.append(func)
        @wraps(func)
        def wrapper(*args, **kwargs):

            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
