import ast
import os.path
import subprocess
from typing import Set

import pytest

class PytestNameVisitor(ast.NodeVisitor):
    def __init__(self, variable: str) -> None:
        super().__init__()
        self.marks: Set[str] = set()
        self._variable = variable

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == self._variable:
                if not isinstance(node.value, (ast.List, ast.Tuple)):
                    raise Exception('bad')
                for elt in node.value.elts:
                    # ast.Constant used since 3.8. ast.Str used before
                    if hasattr(elt, 'value'):
                        self.marks.add(elt.value)
                    elif hasattr(elt, 's'):
                        self.marks.add(elt.s)


class Inspector:
    def __init__(self, fname, variable):
        self._fname = fname
        self._visitor = None
        self._variable = variable

    def inspect(self):
        with open(self._fname, 'r') as f:
            tree = ast.parse(f.read())
        self._visitor = PytestNameVisitor(self._variable)
        self._visitor.visit(tree)

    def report(self):
        assert self._visitor is not None, 'Inspect must be run before calling report()'
        return self._visitor.marks



def pytest_addoption(parser):
    group = parser.getgroup('filemarker')
    group._addoption(
        '--filemarker-active', action="store_true", dest="active", default=False,
        help='Should the plugin be active'
    )
    group._addoption('--filemarker-marks', dest='marks', nargs='+',
        help='Marks to include. Note this is a list of mark names, not expressions'
    )

    group._addoption('--filemarker-files', dest='files', nargs='+',
        help='Files to search. If not supplied will look at the latest changes from git.'
    )

    group._addoption('--filemarker-variable-name', dest='variable',
        help='Files to search. If not supplied will look at the latest changes from git.'
    )

    parser.addini('filemarker_variable', help='joetest')

class FileMarkerPlugin:
    def __init__(self, variable, marks=None, files=None) -> None:
        if marks is None:
            marks = set()
        else:
            marks = set(marks)

        if files is None:
            cmd = ['git', 'diff', '--name-only', '@{1}']
            files = subprocess.check_output(cmd, encoding='utf8').split()
            files = [f for f in files if f.endswith('.py') and os.path.isfile(f)]
        self._marks = marks
        for f in files:
            inspector = Inspector(f, variable)
            inspector.inspect()
            self._marks.update(inspector.report())

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, session, config, items) -> None:
        # Any of the specified marks should be run
        marks = ' or '.join(self._marks)
        markexpr = config.getoption('markexpr')

        # Add on to marks passed in if supplied
        if markexpr and marks:
            markexpr = f'{markexpr} or {marks}'
        elif marks:
            markexpr = marks

        # Update the marks. Otherwise, skip all tests.
        if markexpr:
            config.option.markexpr = markexpr
        else:
            config.hook.pytest_deselected(items=items)
            items[:] = []


def pytest_configure(config):
    active = config.getoption("active")
    variable = config.getoption('variable')
    marks = config.getoption('marks')
    files = config.getoption('files')

    active = active or any([variable, marks, files])

    if variable is None:
        variable = config.getini('filemarker_variable') or 'PYTEST_MARKS'

    if active:
        plugin = FileMarkerPlugin(
            variable, marks=marks, files=files
        )
        config.pluginmanager.register(plugin, "_filemarker")
