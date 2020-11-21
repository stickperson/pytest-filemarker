# pytest-filemarker

A [pytest](https://docs.pytest.org/en/stable/) plugin that runs marked tests when files change.

![Tests](https://github.com/stickperson/pytest-filemarker/workflows/Tests/badge.svg) [![Downloads](https://pepy.tech/badge/pytest-filemarker)](https://pepy.tech/project/pytest-filemarker)

## Usage
Files should have a `PYTEST_MARKS` variable containing a list of marked tests to run when the files change.

```
PYTEST_MARKS = ['markone', 'marktwo']

class MyClass:
    ...
```
When this file has changed, any tests with marks `markone` or `marktwo` will be run.

To invoke the plugin, run:

```
pytest --filemarker-active
```

By default, the plugin will use `git` to look at the changes between `HEAD` and `HEAD~1` to generate a list of files to inspect. To override this, use the `--filemarker-files` parameter:

```
pytest --filemarker-files='<file1> <file2>'
```

## Options
```
filemarker:
  --filemarker-active   Should the plugin be active? Automatically set to True
                        if other options are specified.
  --filemarker-files='file1 file2...'
                        Files to search. If not supplied will look at the latest
                        changes from git.
  --filemarker-variable=VARIABLE
                        Variable which contains a list of marks. Defaults to
                        PYTEST_MARKS
```

`filemarker-variable` can also be set wherever you configure pytest (e.g. `pytest.ini`).
