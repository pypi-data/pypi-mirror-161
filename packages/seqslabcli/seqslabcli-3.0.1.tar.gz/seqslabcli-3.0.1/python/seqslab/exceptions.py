from termcolor import cprint
import errno
import requests
import json


def async_exception_handler(func):
    async def inner_function(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TypeError as error:
            cprint(f"{error}", "red")
            return errno.ENOENT
        except OSError as error:
            cprint(f"{error}", "red")
            return errno.ENOENT
        except requests.HTTPError as error:
            cprint(f"{error}", "red")
            return errno.ECONNREFUSED
        except LookupError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except NotImplementedError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except json.decoder.JSONDecodeError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except ValueError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except AssertionError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL

    return inner_function


def exception_handler(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as error:
            cprint(f"{error}", "red")
            return errno.ENOENT
        except requests.HTTPError as error:
            cprint(f"{error}", "red")
            return errno.ECONNREFUSED
        except OSError as error:
            cprint(f"{error}", "red")
            return errno.ENOENT
        except LookupError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except NotImplementedError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except json.decoder.JSONDecodeError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except ValueError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except AssertionError as error:
            cprint(f"{error}", "red")
            return errno.EINVAL
        except PermissionError as error:
            cprint(f"{error}", "red")
            return errno.EACCES

    return inner_function
