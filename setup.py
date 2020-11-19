from setuptools import setup

setup(
    name="pytest-filemarker",
    packages=["pytest_filemarker"],
    # the following makes a plugin available to pytest
    entry_points={"pytest11": ["filemarker = pytest_filemarker.plugin"]},
    classifiers=["Framework :: Pytest"],
)
