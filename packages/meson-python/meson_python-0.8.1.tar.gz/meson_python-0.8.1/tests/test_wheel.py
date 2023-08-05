# SPDX-License-Identifier: MIT

import os
import platform
import re
import subprocess
import sys
import sysconfig

import pytest
import wheel.wheelfile


EXT_SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')
INTERPRETER_VERSION = f'{sys.version_info[0]}{sys.version_info[1]}'


if platform.python_implementation() == 'CPython':
    INTERPRETER_TAG = f'cp{INTERPRETER_VERSION}'
    PYTHON_TAG = INTERPRETER_TAG
    # Py_UNICODE_SIZE has been a runtime option since Python 3.3,
    # so the u suffix no longer exists
    if sysconfig.get_config_var('Py_DEBUG'):
        INTERPRETER_TAG += 'd'
    # https://github.com/pypa/packaging/blob/5984e3b25f4fdee64aad20e98668c402f7ed5041/packaging/tags.py#L147-L150
    if sys.version_info < (3, 8):
        pymalloc = sysconfig.get_config_var('WITH_PYMALLOC')
        if pymalloc or pymalloc is None:  # none is the default value, which is enable
            INTERPRETER_TAG += 'm'
elif platform.python_implementation() == 'PyPy':
    INTERPRETER_TAG = f'pypy3_{INTERPRETER_VERSION}'
    PYTHON_TAG = f'pp{INTERPRETER_VERSION}'
else:
    raise NotImplementedError(f'Unknown implementation: {platform.python_implementation()}')

PLATFORM_TAG = sysconfig.get_platform().replace('-', '_').replace('.', '_')

if platform.system() == 'Linux':
    SHARED_LIB_EXT = 'so'
elif platform.system() == 'Darwin':
    SHARED_LIB_EXT = 'dylib'
elif platform.system() == 'Windows':
    SHARED_LIB_EXT = 'dll.a'
else:
    raise NotImplementedError(f'Unknown system: {platform.system()}')


def wheel_contents(artifact):
    # Sometimes directories have entries, sometimes not, so we filter them out.
    return {
        entry for entry in artifact.namelist()
        if not entry.endswith('/')
    }


@pytest.mark.skipif(platform.system() != 'Linux', reason='Needs library vendoring, only implemented in POSIX')
def test_contents(package_library, wheel_library):
    artifact = wheel.wheelfile.WheelFile(wheel_library)

    for name, regex in zip(sorted(wheel_contents(artifact)), [
        re.escape(f'.library.mesonpy.libs/libexample.{SHARED_LIB_EXT}'),
        re.escape('library-1.0.0.data/headers/examplelib.h'),
        re.escape('library-1.0.0.data/scripts/example'),
        re.escape('library-1.0.0.dist-info/METADATA'),
        re.escape('library-1.0.0.dist-info/RECORD'),
        re.escape('library-1.0.0.dist-info/WHEEL'),
        rf'library\.libs/libexample.*\.{SHARED_LIB_EXT}',
    ]):
        assert re.match(regex, name), f'`{name}` does not match `{regex}`'


@pytest.mark.xfail(reason='Meson bug')
def test_purelib_and_platlib(wheel_purelib_and_platlib):
    artifact = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib)

    expecting = {
        f'plat{EXT_SUFFIX}',
        'purelib_and_platlib-1.0.0.data/purelib/pure.py',
        'purelib_and_platlib-1.0.0.dist-info/METADATA',
        'purelib_and_platlib-1.0.0.dist-info/RECORD',
        'purelib_and_platlib-1.0.0.dist-info/WHEEL',
    }
    if platform.system() == 'Windows':
        expecting.add('plat{}'.format(EXT_SUFFIX.replace('pyd', 'dll.a')))

    assert wheel_contents(artifact) == expecting


def test_pure(wheel_pure):
    artifact = wheel.wheelfile.WheelFile(wheel_pure)

    assert wheel_contents(artifact) == {
        'pure-1.0.0.dist-info/METADATA',
        'pure-1.0.0.dist-info/RECORD',
        'pure-1.0.0.dist-info/WHEEL',
        'pure.py',
    }


def test_configure_data(wheel_configure_data):
    artifact = wheel.wheelfile.WheelFile(wheel_configure_data)

    assert wheel_contents(artifact) == {
        'configure_data-1.0.0.data/platlib/configure_data.py',
        'configure_data-1.0.0.dist-info/METADATA',
        'configure_data-1.0.0.dist-info/RECORD',
        'configure_data-1.0.0.dist-info/WHEEL',
    }


@pytest.mark.xfail(reason='Meson bug')
def test_interpreter_abi_tag(wheel_purelib_and_platlib):
    expected = f'purelib_and_platlib-1.0.0-{PYTHON_TAG}-{INTERPRETER_TAG}-{PLATFORM_TAG}.whl'
    assert wheel_purelib_and_platlib.name == expected


@pytest.mark.skipif(platform.system() != 'Linux', reason='Unsupported on this platform for now')
@pytest.mark.xfail(
    sys.version_info >= (3, 9) and os.environ.get('GITHUB_ACTIONS') == 'true',
    reason='github actions',
    strict=True,
)
def test_local_lib(virtual_env, wheel_link_against_local_lib):
    subprocess.check_call([virtual_env, '-m', 'pip', 'install', wheel_link_against_local_lib])
    subprocess.check_output([
        virtual_env, '-c', 'import example; print(example.example_sum(1, 2))'
    ]).decode() == '3'


def test_contents_license_file(wheel_license_file):
    artifact = wheel.wheelfile.WheelFile(wheel_license_file)
    assert artifact.read('license_file-1.0.0.dist-info/LICENSE.custom').rstrip() == b'Hello!'
