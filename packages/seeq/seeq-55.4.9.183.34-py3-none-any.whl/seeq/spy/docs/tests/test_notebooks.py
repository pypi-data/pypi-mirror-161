"""Smoke test ensuring that example notebooks run without error."""

import concurrent.futures
import os
import pathlib
import re

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

from seeq.base import system
from seeq.spy.tests import test_common

THIS_DIR = pathlib.Path(__file__).absolute().parent
DOCUMENTATION_DIR = THIS_DIR / ".." / "Documentation"


def setup_module():
    test_common.initialize_sessions()


def load_notebook(path):
    with open(path, encoding='utf-8') as f:
        return nbformat.read(f, as_version=4)


def run_notebook(notebook_name):
    print(f'Running Jupyter Notebook "{notebook_name}"')

    # 7-bit C1 ANSI sequences
    def escape_ansi_control(error):
        ansi_escape = re.compile(r'''
            \x1B    # ESC
            [@-_]   # 7-bit C1 Fe
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        ''', re.VERBOSE)
        sanitized = ""
        for line in error:
            sanitized += ansi_escape.sub('', line) + "\n"
        return sanitized

    path = os.path.normpath(DOCUMENTATION_DIR / notebook_name)
    nb = load_notebook(path)

    all_cells = nb['cells']

    for cell_index in range(len(all_cells)):
        # Replace cells that contain set_trace with print
        source = all_cells[cell_index]['source']
        if 'set_trace()' in source:
            # Convert to dictionary to modify content
            content_to_modify = dict(all_cells[cell_index])
            content_to_modify['source'] = "#print('skip_cell_because_of_set_trace_function')"
            nb['cells'][cell_index] = nbformat.from_dict(content_to_modify)

    proc = ExecutePreprocessor(timeout=1200)
    proc.allow_errors = True
    system.do_with_retry(
        lambda: proc.preprocess(nb, {'metadata': {'path': os.path.dirname(path)}}),
        timeout_sec=1200)

    for cell in nb.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    pytest.fail("\nNotebook '{}':\n{}".format(notebook_name, escape_ansi_control(output.traceback)))


def check_links(notebook_name):
    print(f'Checking links in Jupyter Notebook "{notebook_name}"')

    path = os.path.normpath(DOCUMENTATION_DIR / notebook_name)
    nb = load_notebook(path)

    all_cells = nb['cells']

    for cell_index in range(len(all_cells)):
        source = all_cells[cell_index]['source']

        if all_cells[cell_index]['cell_type'] != 'markdown':
            continue

        for match in re.finditer(r'(\[[^]]+]\((.*?\.ipynb)\))', source):
            link = match.group(1)
            ipynb_file = match.group(2).replace('%20', ' ')
            path_to_ipynb = os.path.join(os.path.dirname(path), ipynb_file)
            if not os.path.exists(path_to_ipynb):
                pytest.fail(f'Link in cell {cell_index} of "{path}" has broken link:\n{link}')

        match = re.match(r'.*(seeq\.atlassian\.net/wiki).*', source)
        if match:
            pytest.fail(f'Old support website link found in cell {cell_index} of "{path}":\n{source}')


def cleanup_files(files_to_cleanup):
    for file_to_cleanup in files_to_cleanup:
        if os.path.exists(file_to_cleanup):
            if os.path.isfile(file_to_cleanup):
                os.remove(file_to_cleanup)
            else:
                system.removetree(file_to_cleanup)


def scan_for_notebooks(only_runnable=False):
    for root, dirs, files in os.walk(DOCUMENTATION_DIR):
        for file in files:
            if not file.endswith(".ipynb"):
                continue

            if file.endswith("-checkpoint.ipynb"):
                continue

            if only_runnable:
                if "spy.jobs.ipynb" in file or "spy.login.ipynb" in file or "Advanced Scheduling" in root:
                    continue

            yield os.path.relpath(os.path.join(root, file), DOCUMENTATION_DIR)


@pytest.mark.system
def test_notebook_links():
    notebooks = scan_for_notebooks()
    for notebook in notebooks:
        check_links(notebook)


@pytest.mark.system
def test_run_notebooks():
    notebooks = scan_for_notebooks(only_runnable=True)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            _futures = list()
            for notebook in notebooks:
                _futures.append(executor.submit(run_notebook, notebook))

            concurrent.futures.wait(_futures)

            for _future in _futures:
                if _future.exception():
                    raise _future.exception()

    finally:
        cleanup_files([DOCUMENTATION_DIR / 'pickled_search.pkl',
                       DOCUMENTATION_DIR / 'pickled_pull.pkl',
                       DOCUMENTATION_DIR / '..' / 'My First Export'])
