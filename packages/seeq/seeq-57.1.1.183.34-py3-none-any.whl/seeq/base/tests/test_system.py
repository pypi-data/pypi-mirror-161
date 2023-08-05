import os
import tempfile
import textwrap
from pathlib import Path

import configuration.helpers as conf
import pytest

from seeq.base import system
from seeq.base.system import human_readable_byte_count


@pytest.mark.unit
def test_human_readable_byte_count_base_ten():
    '''
    Make sure we get the same results as SystemInfoTest#testHumanReadableByteCountBaseTen
    '''
    assert human_readable_byte_count(0, False, False) == '0 B'
    assert human_readable_byte_count(10, False, False) == '10 B'
    assert human_readable_byte_count(900, False, False) == '900 B'
    assert human_readable_byte_count(999, False, False) == '999 B'

    assert human_readable_byte_count(1000, False, False) == '1.00 KB'
    assert human_readable_byte_count(2000, False, False) == '2.00 KB'
    assert human_readable_byte_count(1000 * 1000 - 10, False, False) == '999.99 KB'

    assert human_readable_byte_count(1000 * 1000, False, False) == '1.00 MB'
    assert human_readable_byte_count(50 * 1000 * 1000, False, False) == '50.00 MB'
    assert human_readable_byte_count(1000 * 1000 * 1000 - 10000, False, False) == '999.99 MB'

    assert human_readable_byte_count(1000 * 1000 * 1000, False, False) == '1.00 GB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000, False, False) == '50.00 GB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 - 10000000, False, False) == '999.99 GB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000, False, False) == '1.00 TB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 TB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 - 1e10, False, False) == '999.99 TB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000, False, False) == '1.00 PB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 PB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000 - 1e13, False, False) == '999.99 PB'

    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '1.00 EB'
    assert human_readable_byte_count(50 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000, False, False) == '50.00 EB'
    assert human_readable_byte_count(1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 - 1e16, False, False) == '999.99 EB'


@pytest.mark.unit
def test_spawn_list_args():
    """
    Spawns process which writes each argument in argv to a JSON file.
    That file is read back and verified that all arguments were correctly preserved.
    """
    import json

    script = textwrap.dedent(r'''
        import json, os, sys
        with open(os.getenv('_TEST_FILE_'), 'w') as f:
            json.dump(sys.argv[1:], f)
    ''')

    args = ['foo', 'Giving "NIFTY" quotes', 'Making $dollars and', ' taking\na %percent%(!) ']
    with tempfile.TemporaryDirectory() as temp:
        out_file = os.path.join(temp, f'received args.json')
        system.spawn(['python', '-c', script, *args], env={**os.environ, '_TEST_FILE_': str(out_file)})

        with open(out_file, 'r') as f:
            loaded = json.load(f)

        assert loaded == args


@pytest.mark.unit
def test_calculate_default_optimal_heap_sizes():
    # cores, physical, appserver, jmvLink, postgres, netLink, renderer, reverse proxy, supervisor, os
    matrix_cols = [
        'Cpu/Count',
        'Memory/System/Total',
        'Memory/Appserver/Size',
        'Memory/JvmLink/Size',
        'Memory/Postgres/Size',
        'Memory/NetLink/Size',
        'Memory/Renderer/Size',
        'Memory/ReverseProxy/Size',
        'Memory/Supervisor/Size',
        'Memory/OperatingSystem/Size',
        'Memory/CacheService/Series/Size',
        'Memory/CacheService/Series/Postgres/Size',
        'Memory/CacheService/Scalar/Size',
        'Memory/FormulaSupport/Size',
        'Memory/Auth/Postgres/Size',
        "Components/MessagingService/Enabled",
        "Memory/MessagingService/Size",
        "Components/DatasourceProxyService/Enabled",
        "Memory/DatasourceProxyService/Size",
    ]

    test_matrix = [
        # 64-bit, 8 cpu cores for screenshot purposes
        # P Total Appsr JvmL PG    NetL Rend Proxy Sup OS SrCch SrPG ScCch FS AuPG MsgEn  Msg  DAEn   DA
        [8, 4000, 1000, 250, 2250, 250, 500, 200, 300, 800, 160, 200, 100, 50, 200, False, 200, False, 512],
        [8, 8000, 2000, 500, 2250, 500, 1000, 200, 300, 1600, 160, 200, 100, 50, 200, False, 200, False, 512],
        [8, 12000, 3140, 750, 2250, 750, 1500, 200, 300, 2400, 160, 200, 100, 50, 200, False, 200, False, 1024],
        [8, 16000, 4598, 1000, 2992, 1000, 2000, 200, 300, 3200, 160, 200, 100, 50, 200, False, 200, False, 1024],
        [8, 32000, 10406, 2000, 5984, 2000, 4000, 200, 300, 6400, 160, 200, 100, 50, 200, False, 200, False, 2048],
        [8, 64000, 26022, 4000, 11968, 4000, 4000, 200, 300, 12800, 160, 200, 100, 50, 200, False, 200, False, 2048],
        [8, 128000, 57254, 8000, 23936, 8000, 4000, 200, 300, 25600, 160, 200, 100, 50, 200, False, 200, False, 2048],
        [8, 256000, 119718, 16000, 47872, 16000, 4000, 200, 300, 51200, 160, 200, 100, 50, 200, False, 200, False, 2048],
        # Messaging Service and Datasource Proxy service Enabled
        [8, 4000, 1000, 250, 2250, 250, 500, 200, 300, 800, 160, 200, 100, 50, 200, True, 200, True, 512],
        [8, 8000, 2000, 500, 2250, 500, 1000, 200, 300, 1600, 160, 200, 100, 50, 200, True, 200, True, 512],
        [8, 12000, 3000, 750, 2250, 750, 1500, 200, 300, 2400, 160, 200, 100, 50, 200, True, 200, True, 1024],
        [8, 16000, 4000, 1000, 2992, 1000, 2000, 200, 300, 3200, 160, 200, 100, 50, 200, True, 200, True, 1024],
        [8, 32000, 8158, 2000, 5984, 2000, 4000, 200, 300, 6400, 160, 200, 100, 50, 200, True, 200, True, 2048],
        [8, 64000, 23774, 4000, 11968, 4000, 4000, 200, 300, 12800, 160, 200, 100, 50, 200, True, 200, True, 2048],
        [8, 128000, 55006, 8000, 23936, 8000, 4000, 200, 300, 25600, 160, 200, 100, 50, 200, True, 200, True, 2048],
        [8, 256000, 117470, 16000, 47872, 16000, 4000, 200, 300, 51200, 160, 200, 100, 50, 200, True, 200, True, 2048],

        # 64-bit, 64 cpu cores for screenshot purposes
        [64, 4000, 1000, 250, 2250, 250, 500, 400, 300, 800, 1280, 200, 100, 50, 200, False, 640, False, 512],
        [64, 8000, 2000, 500, 2250, 500, 1000, 400, 300, 1600, 1280, 200, 100, 50, 200, False, 640, False, 512],
        [64, 12000, 3000, 750, 2250, 750, 1500, 400, 300, 2400, 1280, 200, 100, 50, 200, False, 640, False, 1024],
        [64, 16000, 4000, 1000, 2992, 1000, 2000, 400, 300, 3200, 1280, 200, 100, 50, 200, False, 640, False, 1024],
        [64, 32000, 9086, 2000, 5984, 2000, 4000, 400, 300, 6400, 1280, 200, 100, 50, 200, False, 640, False, 8000],
        [64, 64000, 20702, 4000, 11968, 4000, 8000, 400, 300, 12800, 1280, 200, 100, 50, 200, False, 640, False, 16000],
        [64, 128000, 43934, 8000, 23936, 8000, 16000, 400, 300, 25600, 1280, 200, 100, 50, 200, False, 640, False, 16384],
        [64, 256000, 90398, 16000, 47872, 16000, 32000, 400, 300, 51200, 1280, 200, 100, 50, 200, False, 640, False, 16384],
        [64, 512000, 215326, 32000, 95744, 32000, 32000, 400, 300, 102400, 1280, 200, 100, 50, 200, False, 640, False, 16384],
        # Messaging Service and Datasource Proxy service Enabled
        [64, 4000, 1000, 250, 2250, 250, 500, 400, 300, 800, 1280, 200, 100, 50, 200, True, 640, True, 512],
        [64, 8000, 2000, 500, 2250, 500, 1000, 400, 300, 1600, 1280, 200, 100, 50, 200, True, 640, True, 512],
        [64, 12000, 3000, 750, 2250, 750, 1500, 400, 300, 2400, 1280, 200, 100, 50, 200, True, 640, True, 1024],
        [64, 16000, 4000, 1000, 2992, 1000, 2000, 400, 300, 3200, 1280, 200, 100, 50, 200, True, 640, True, 1024],
        [64, 32000, 8000, 2000, 5984, 2000, 4000, 400, 300, 6400, 1280, 200, 100, 50, 200, True, 640, True, 8000],
        [64, 64000, 16000, 4000, 11968, 4000, 8000, 400, 300, 12800, 1280, 200, 100, 50, 200, True, 640, True, 16000],
        [64, 128000, 32000, 8000, 23936, 8000, 16000, 400, 300, 25600, 1280, 200, 100, 50, 200, True, 640, True, 16384],
        [64, 256000, 73374, 16000, 47872, 16000, 32000, 400, 300, 51200, 1280, 200, 100, 50, 200, True, 640, True, 16384],
        [64, 512000, 198302, 32000, 95744, 32000, 32000, 400, 300, 102400, 1280, 200, 100, 50, 200, True, 640, True, 16384]
    ]

    def get_heap_sizes(cpu, memory, is_msg_enabled, is_datasource_proxy_enabled):
        conf.set_option('Cpu/Count', cpu, '')
        conf.set_option('Memory/System/Total', memory, '')
        conf.set_option('Components/MessagingService/Enabled', is_msg_enabled, '')
        conf.set_option('Components/DatasourceProxyService/Enabled', is_datasource_proxy_enabled, '')

        return [conf.get_option(path) for path in matrix_cols]

    with conf.overriding_config({path: None for path in matrix_cols}):
        actual_matrix = [get_heap_sizes(cpu, memory, is_msg_enabled, is_datasource_proxy_enabled)
                         for [cpu, memory, *_, is_msg_enabled, _, is_datasource_proxy_enabled, _] in test_matrix
                         ]

    # Uncomment the following to help with updating the test
    # import pprint
    # print(pprint.pformat(actual_matrix))
    # assert False

    assert actual_matrix == test_matrix


@pytest.mark.unit
def test_replace_in_file():
    with tempfile.TemporaryDirectory() as temp:
        service_file = os.path.join(temp, f'bogus.service')
        if not os.path.exists(service_file):
            with open(service_file, 'w') as f:
                f.write(textwrap.dedent(f"""
                    [Service]
                    Type=simple
                    User=mark
                    ExecStart=/opt/seeq/seeq start --from-service
                    ExecStop=/opt/seeq/seeq stop
                    Restart=on-failure

                    [Install]
                    WantedBy=multi-user.target
                """))

        system.replace_in_file(service_file, [
            (r'User=.*', 'User=alan'),
            (r'ExecStart=.*', 'ExecStart=/stuff/seeq start --from-service'),
            (r'ExecStop=.*', 'ExecStop=/stuff/seeq stop')
        ])

        with open(service_file, 'r') as f:
            content = f.read()
            assert 'User=alan' in content
            assert 'ExecStart=/stuff/seeq start --from-service' in content
            assert 'ExecStop=/stuff/seeq stop' in content


@pytest.mark.unit
def test_copy_tree_exclude_folder_relative_path():
    # It was discovered in CRAB-20621 that robocopy's /XD flag to exclude directories wasn't working for relative
    # paths to subdirectories. This tests system#copy_tree to be compatible with non-Windows systems.
    # See https://superuser.com/a/690842 and follow-up comments
    with tempfile.TemporaryDirectory() as src:
        tree = DirectoryTestTree(src)
        with tempfile.TemporaryDirectory() as dest:
            system.copytree(src, dest, exclude=tree.exclude)

            all_root_contents = os.listdir(dest)
            # Destination should only have KeepParent and KeepMe.txt
            assert len(all_root_contents) == 2
            assert str(tree.keep_parent_dir_relative) in all_root_contents
            assert tree.root_keep_file_name in all_root_contents

            # Destination should have only KeepParent/KeepMe subdir
            all_subdirs = os.listdir(dest / tree.keep_parent_dir_relative)
            assert len(all_subdirs) == 1
            assert tree.keep_subdir_name in all_subdirs


@pytest.mark.unit
def test_copytree_destination_excludes(tmp_path: Path):
    src = tmp_path / 'src'
    dst = tmp_path / 'dst'

    src.mkdir()
    (src / 'dir').mkdir()
    (src / 'dir' / 'file.txt').touch()
    (src / 'dir2').mkdir()
    (src / 'dir2' / 'file2.txt').touch()
    (src / 'dir3').mkdir()
    (src / 'dir3' / 'file3.txt').touch()
    (src / 'file4.txt').touch()
    (src / 'file5.txt').touch()
    dst.mkdir()
    (dst / 'important').mkdir()
    (dst / 'important' / 'secrets.txt').touch()
    system.copytree(str(src), str(dst), mirror=True, exclude=['dir', 'important'])
    assert not (dst / 'dir').exists()
    assert not (dst / 'dir' / 'file.txt').exists()
    assert (dst / 'dir2').exists()
    assert (dst / 'dir2' / 'file2.txt').exists()
    assert (dst / 'dir3').exists()
    assert (dst / 'dir3' / 'file3.txt').exists()
    assert (dst / 'file4.txt').exists()
    assert (dst / 'file5.txt').exists()
    assert (dst / 'important').exists()
    assert (dst / 'important' / 'secrets.txt').exists()


@pytest.mark.unit
def test_removetree_keep_top(tmp_path: Path):
    (tmp_path / 'dir').mkdir()
    (tmp_path / 'dir' / 'file.txt').touch()
    (tmp_path / 'file2.txt').touch()
    system.removetree(str(tmp_path), keep_top_folder=True)
    assert not (tmp_path / 'dir').exists()
    assert not (tmp_path / 'dir' / 'file.txt').exists()
    assert not (tmp_path / 'file2.txt').exists()
    assert tmp_path.exists()


@pytest.mark.unit
def test_removetree_with_exclusions(tmp_path: Path):
    (tmp_path / 'dir').mkdir()
    (tmp_path / 'dir' / 'file.txt').touch()
    (tmp_path / 'dir2').mkdir()
    (tmp_path / 'dir2' / 'file2.txt').touch()
    (tmp_path / 'dir3').mkdir()
    (tmp_path / 'dir3' / 'file3.txt').touch()
    (tmp_path / 'file4.txt').touch()
    (tmp_path / 'file5.txt').touch()
    system.removetree(str(tmp_path), exclude_subdirectories=['dir'])
    assert (tmp_path / 'dir').exists()
    assert (tmp_path / 'dir' / 'file.txt').exists()
    assert not (tmp_path / 'dir2').exists()
    assert not (tmp_path / 'dir2' / 'file2.txt').exists()
    assert not (tmp_path / 'dir3').exists()
    assert not (tmp_path / 'dir3' / 'file3.txt').exists()
    assert not (tmp_path / 'file4.txt').exists()
    assert not (tmp_path / 'file5.txt').exists()
    system.removetree(str(tmp_path), exclude_subdirectories=['nonexistant'])
    assert not (tmp_path / 'dir').exists()
    assert not (tmp_path / 'dir' / 'file.txt').exists()
    assert tmp_path.exists()


class DirectoryTestTree():
    def __init__(self, root):
        self.root = root
        self.keep_parent_dir_relative = Path('KeepParent')
        self.keep_subdir_name = 'KeepMe'
        self.exclude_subdir_name = 'ExcludeMe'
        self.exclude_parent_dir_relative = Path('ExcludeParent')

        self.root_keep_file_name = 'KeepMe.txt'
        self.root_exclude_file_name = 'ExcludeMe.txt'

        self.keep_subdir_relative = self.keep_parent_dir_relative / self.keep_subdir_name
        self.exclude_subdir_relative = self.keep_parent_dir_relative / self.exclude_subdir_name

        self.exclude = [str(self.exclude_parent_dir_relative), str(self.exclude_subdir_relative),
                        self.root_exclude_file_name]

        self._create_tree()

    def _create_tree(self):
        # tmpDir
        # |
        # ---- KeepMe.txt
        # -----ExcludeMe.txt
        # ---- ExcludeParent
        # ---- KeepParent
        #          |
        #          ----- KeepMe
        #          |
        #          ----- ExcludeMe
        os.makedirs(self.root / self.keep_subdir_relative)
        os.makedirs(self.root / self.exclude_parent_dir_relative)
        os.makedirs(self.root / self.exclude_subdir_relative)

        open(Path(self.root) / self.root_keep_file_name, 'a').close()
        open(Path(self.root) / self.root_exclude_file_name, 'a').close()


def main(cpu_count, total_memory_mb):
    memory_configurations = [
        'Cpu/Count',
        'Memory/System/Total',
        'Memory/Appserver/Size',
        'Memory/JvmLink/Size',
        'Memory/Postgres/Size',
        '   Database/Postgres/SharedBuffers',
        '   Database/Postgres/EffectiveCacheSize',
        '   Database/Postgres/WorkMem',
        '   Database/Postgres/MaintenanceWorkMem',
        'Memory/NetLink/Size',
        'Memory/Renderer/Size',
        'Memory/ReverseProxy/Size',
        'Memory/Supervisor/Size',
        'Memory/OperatingSystem/Size'
    ]
    conf.set_option('Cpu/Count', cpu_count, '')
    conf.set_option('Memory/System/Total', total_memory_mb, '')
    print()
    for path in memory_configurations:
        print("%s%s" % (path.ljust(40, ' '), str(conf.get_option(path.lstrip())).rjust(8, ' ')))

    conf.unset_option('Cpu/Count')
    conf.unset_option('Memory/System/Total')


if __name__ == "__main__":
    main(64, 32768)
