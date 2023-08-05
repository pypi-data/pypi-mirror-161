import os
import tempfile
from distutils import dir_util
from unittest.mock import patch

import pytest

from seeq.base import system
from seeq.spy.docs import _copy


@pytest.mark.unit
def test_copy():
    with tempfile.TemporaryDirectory() as temp_folder:
        long_folder_name = os.path.join(temp_folder, 'long_' * 10)
        _copy.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        for file_name in _copy.ADVANCED_ONLY_FILES:
            assert not os.path.exists(os.path.join(long_folder_name, file_name))

        with pytest.raises(RuntimeError):
            _copy.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        _copy.copy(long_folder_name, overwrite=True, advanced=True)

        assert os.path.exists(long_folder_name)
        assert os.path.exists(os.path.join(long_folder_name, 'spy.workbooks.ipynb'))
        assert os.path.exists(os.path.join(long_folder_name, 'Asset Trees 3 - Report and Dashboard Templates.ipynb'))

        system.removetree(long_folder_name)


@pytest.mark.unit
def test_copy_missing_advanced():
    with tempfile.TemporaryDirectory() as temp_folder:
        long_folder_name = os.path.join(temp_folder, 'long_' * 10)

        def os_remove_mock(path):
            if _copy.ADVANCED_ONLY_FILES[0] in path:
                raise FileNotFoundError

        def dir_util_remove_tree_mock(path):
            if _copy.ADVANCED_ONLY_DIRS[0] in path:
                raise FileNotFoundError

        with patch('os.remove'), patch('distutils.dir_util.remove_tree'):
            os.remove.side_effect = os_remove_mock
            dir_util.remove_tree.side_effect = dir_util_remove_tree_mock
            with pytest.warns(RuntimeWarning) as record:
                _copy.copy(long_folder_name)

        assert len(record) == 2
        assert _copy.ADVANCED_ONLY_FILES[0] in record[0].message.args[0]
        assert _copy.ADVANCED_ONLY_DIRS[0] in record[1].message.args[0]

        assert os.path.exists(long_folder_name)

        system.removetree(long_folder_name)
