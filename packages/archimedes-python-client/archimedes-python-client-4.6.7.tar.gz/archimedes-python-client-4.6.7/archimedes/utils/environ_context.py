import os
from contextlib import contextmanager


@contextmanager
def environ(env):
    """Temporarily set environment variables inside the context manager and
    fully restore previous environment afterwards

    Borrowed from here: https://gist.github.com/igniteflow/7267431

    Example usage:
    print(os.environ['USER']) # prints username of current user

    user_temporary = "temp_user"
    with environ({"USER": user_temporary}):
        print(os.environ['USER']) # prints "temp_user"

    print(os.environ['USER']) # prints username of current user
    """
    original_env = {key: os.getenv(key) for key in env}
    os.environ.update(env)
    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value
