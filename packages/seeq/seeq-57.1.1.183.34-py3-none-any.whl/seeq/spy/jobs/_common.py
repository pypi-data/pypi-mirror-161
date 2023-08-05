from __future__ import annotations

import logging
import os
import requests
import sys
from nbformat import NotebookNode
from seeq.spy._session import Session

DEFAULT_REQUESTS_TIMEOUT = 90

# Logger to be used for logging inside executor container
executor_logger = None


def _setup_executor_logging():
    global executor_logger
    log_level = get_log_level_from_executor()

    # python logging doesnt have TRACE
    log_level = "DEBUG" if log_level == "TRACE" else log_level

    executor_logger = logging.getLogger("executor_logger")
    exec_handler = logging.StreamHandler(sys.stdout)
    exec_formatter = logging.Formatter('%(levelname)s - %(message)s')

    exec_handler.setFormatter(exec_formatter)
    executor_logger.addHandler(exec_handler)

    executor_logger.setLevel(log_level)

    return executor_logger


def get_executor_logger():
    global executor_logger

    if executor_logger is not None:
        return executor_logger
    else:
        return _setup_executor_logging()


def get_log_level_from_executor():
    return str(os.environ.get('LOG_LEVEL', 'INFO')).upper()


def is_log_level_trace_from_executor():
    return get_log_level_from_executor() == "TRACE"


def running_in_datalab():
    return os.environ.get('SEEQ_SDL_CONTAINER_IS_DATALAB') == 'true'


def running_in_executor():
    return os.environ.get('SEEQ_SDL_CONTAINER_IS_EXECUTOR') == 'true'


def get_label_from_executor():
    return os.environ.get('SEEQ_SDL_LABEL') or ''


def get_results_folder():
    return "_Job Results/"


def get_cell_execution_timeout():
    return 86400


def get_execution_notebook(lang: str) -> str:
    path = "/seeq/scheduling"
    if lang == "python":
        file = os.path.join(path, "ExecutionNotebook.ipynb")
    elif lang == "R":
        file = os.path.join(path, "ExecutionNotebookR.ipynb")
    else:
        raise FileNotFoundError(f"Could not find an execution notebook for language {lang}")

    return file


def get_notebook_language(nb_notebook: NotebookNode) -> str:
    try:
        language = nb_notebook['metadata']['kernelspec']['language']
    except:
        language = None

    return language


def requests_get(session: Session, url, params=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.get(url, params=params, timeout=timeout, verify=session.https_verify_ssl, **kwargs)


def requests_patch(session: Session, url, data=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.patch(url, data=data, timeout=timeout, verify=session.https_verify_ssl, **kwargs)


def requests_post(session: Session, url, data=None, json=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.post(url, data=data, json=json, timeout=timeout, verify=session.https_verify_ssl, **kwargs)


def requests_put(session: Session, url, data=None, timeout=DEFAULT_REQUESTS_TIMEOUT, **kwargs):
    return requests.put(url, data=data, timeout=timeout, verify=session.https_verify_ssl, **kwargs)
