import subprocess
import pytest


pytest_plugins = ("pytester",)


FILE = """
import pytest


def test_unmarked():
    assert True


@pytest.mark.first
def test_first():
    assert True


@pytest.mark.second
def test_second():
    assert True

@pytest.mark.third
def test_third():
    assert True
"""


@pytest.mark.filterwarnings("ignore")
def test_single_file(testdir):
    first = """
        PYTEST_MARKS = ['first', 'third']
    """
    marker = testdir.makepyfile(mark=first)
    test = testdir.makepyfile(test=FILE)
    args = ['-v', f'--filemarker-files={marker}', test]
    result = testdir.runpytest(*args)
    assert result.ret == 0
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines_random([
        '*test.py::test_first PASSED*',
        '*test.py::test_third PASSED*'
    ])


@pytest.mark.filterwarnings("ignore")
def test_file_and_passed_marks(testdir):
    first = """
        PYTEST_MARKS = ['first', 'third']
    """
    marker = testdir.makepyfile(mark=first)
    test = testdir.makepyfile(test=FILE)
    args = ['-v', '-m', 'second', f'--filemarker-files={marker}', test]
    result = testdir.runpytest(*args)
    assert result.ret == 0
    result.assert_outcomes(passed=3)
    result.stdout.fnmatch_lines_random([
        '*test.py::test_first PASSED*',
        '*test.py::test_second PASSED*',
        '*test.py::test_third PASSED*'
    ])


@pytest.mark.filterwarnings("ignore")
def test_multiple_files(testdir):
    first = """
        PYTEST_MARKS = ['first']
    """

    second = """
        PYTEST_MARKS = ['second']
    """
    first_marker = testdir.makepyfile(first=first)
    second_marker = testdir.makepyfile(second=second)
    test = testdir.makepyfile(test=FILE)

    files = f'{first_marker} {second_marker}'
    args = ['-v', f'--filemarker-files={files}', test]
    result = testdir.runpytest(*args)
    assert result.ret == 0
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines_random([
        '*test.py::test_first PASSED*',
        '*test.py::test_second PASSED*'
    ])


@pytest.mark.filterwarnings("ignore")
def test_mark_variable(testdir):
    mark = """
        CUSTOM = ['first', 'third']
    """
    custom = testdir.makepyfile(custom=mark)
    test = testdir.makepyfile(test=FILE)

    args = ['-v', f'--filemarker-files={custom}', '--filemarker-variable=CUSTOM', test]
    result = testdir.runpytest(*args)
    assert result.ret == 0
    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines_random([
        '*test.py::test_first PASSED*',
        '*test.py::test_third PASSED*'
    ])


@pytest.mark.filterwarnings("ignore")
def test_no_marks(testdir):
    f = ''
    marker = testdir.makepyfile(mark=f)
    test = testdir.makepyfile(test=FILE)
    args = ['-v', f'--filemarker-files={marker}', test]
    result = testdir.runpytest(*args)
    assert result.ret == 5
    result.stdout.fnmatch_lines_random([
        '*4 deselected*',
    ])


@pytest.mark.filterwarnings("ignore")
def test_bad_variable(testdir):
    first = """
        PYTEST_MARKS = 'bad'
    """
    marker = testdir.makepyfile(mark=first)
    test = testdir.makepyfile(test=FILE)
    args = [f'--filemarker-files={marker}', test]
    result = testdir.runpytest(*args)
    assert result.ret == 3
    result.stderr.fnmatch_lines_random([
        '*must be a list or tuple*',
    ])


@pytest.mark.filterwarnings("ignore")
def test_active_no_files_passed(testdir, mocker):
    first = """
        PYTEST_MARKS = ['first']
    """
    marker = testdir.makepyfile(mark=first)
    mocker.patch.object(subprocess, 'check_output', return_value=f'{marker}')

    test = testdir.makepyfile(test=FILE)
    args = ['-v', '--filemarker-active', test]
    result = testdir.runpytest(*args)
    assert result.ret == 0
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines_random([
        '*test.py::test_first PASSED*',
    ])


@pytest.mark.filterwarnings("ignore")
def test_not_active_by_default(testdir):
    test = testdir.makepyfile(test=FILE)
    args = ['-v', test]
    result = testdir.runpytest(*args)
    assert result.ret == 0
    result.assert_outcomes(passed=4)
    result.stdout.fnmatch_lines_random([
        '*test.py::test_first PASSED*',
    ])
