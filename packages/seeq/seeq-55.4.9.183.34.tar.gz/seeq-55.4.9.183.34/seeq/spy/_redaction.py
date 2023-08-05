from functools import wraps
from typing import Callable, List, Any

from seeq.spy._common import *
from seeq.spy._status import Status


def request_safely(*,
                   action_description: str = '',
                   errors: str = 'raise',
                   status: Status = None,
                   additional_errors: List[int] = None,
                   on_error: Callable[[str], Any] = None,
                   default_value=None):
    """
    Safely make request(s) to the Seeq API while catching known problematic exceptions. The status codes to be
    caught are 403 (Forbidden), 404 (Not Found), and 500 (Internal Server Error).

    :param action_description: The description for the action(s) being performed. It should include the overall
        purpose and specific information about the item(s) being interacted with. It should be written such that the
        format of 'Failed to [action_description] because...' will be grammatically correct and be meaningful to
        users and Seeq support.
    :param errors: {'raise', 'catalog'} If 'raise', re-raises the exception. If 'catalog', performs the on_error
        action and returns the default_value when the Appserver return status is a known mappable error type.
    :param status: The status object used to log warnings.
    :param additional_errors: Allow these additional HTTP error statuses to be caught. Must be a list of ints.
    :param on_error: A callable to override how to handle an error. Should accept a single string parameter that
        describes the problem. Default behavior is to log a warning to the status.
    :param default_value: The default value to return if a 403, 404, or 500 error occurs.
    :return: The output of the decorated function or default_value if a failure occurred.
    """

    def decorator(func: Callable):
        @wraps(func)
        def out(*args, **kwargs):

            def _no_action(msg):
                pass

            error_action = _no_action
            if callable(on_error):
                error_action = on_error
            elif hasattr(status, 'warn'):
                error_action = status.warn

            try:
                return func(*args, **kwargs)
            except ApiException as e:
                if errors != 'catalog':
                    raise
                reason = get_api_exception_message(e)
                if e.status == 403:
                    error_action(f'Failed to {action_description} due to insufficient access: "{reason}"')
                elif e.status == 404:
                    error_action(f'Failed to {action_description} because it was not found: "{reason}"')
                elif e.status == 500:
                    error_action(f'Failed to {action_description} because an internal server error occurred. '
                                 f'If this persists, please submit logs to Seeq support.')
                elif additional_errors and e.status in additional_errors:
                    error_action(f'Failed to {action_description}: "{reason}"')
                else:
                    # Other statuses (409 particularly) should be re-raised so the normal error handling can work
                    raise
                return default_value

        return out

    return decorator


def safely(func: Callable,
           *,
           action_description: str = '',
           errors: str = 'raise',
           status: Status = None,
           additional_errors: List[int] = None,
           on_error: Callable[[str], Any] = None,
           default_value=None):
    """
    Safely make request(s) to the Seeq API while catching known problematic exceptions. The status codes to be
    caught are 403 (Forbidden), 404 (Not Found), and 500 (Internal Server Error).

    :param func: The function or lambda that will be called with error handling.
    :param action_description: The description for the action(s) being performed. It should include the overall
        purpose and specific information about the item(s) being interacted with. It should be written such that the
        format of 'Failed to [action_description] because...' will be grammatically correct and be meaningful to
        users and Seeq support.
    :param errors: {'raise', 'catalog'} If 'raise', re-raises the exception. If 'catalog', performs the on_error
        action and returns the default_value when the Appserver return status is a known mappable error type.
    :param status: The status object used to log warnings.
    :param additional_errors: Allow these additional HTTP error statuses to be caught. Must be a list of ints.
    :param on_error: A callable to describe how to handle an error. Should accept a single string parameter that
        describes the problem. Default behavior is to log a warning to the status.
    :param default_value: The default value to return if a 403, 404, or 500 error occurs.
    :return: The output of the decorated function or default_value if a failure occurred.
    """
    return request_safely(action_description=action_description,
                          errors=errors,
                          status=status,
                          additional_errors=additional_errors,
                          on_error=on_error,
                          default_value=default_value)(func)()
