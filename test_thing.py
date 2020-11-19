import pytest



PYTEST_MARKS = ['helloworld']


@pytest.mark.helloworld
def test_hello():
    assert True

