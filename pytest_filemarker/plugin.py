import ast
import os.path
import subprocess

class PytestNameVisitor(ast.NodeVisitor):
    def __init__(self, variable) -> None:
        super().__init__()
        self.marks = set()
        self._variable = variable

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if 'id' in target._fields and target.id == self._variable:
                if not isinstance(node.value, ast.List):
                    raise Exception('bad')
                for elt in node.value.elts:
                    self.marks.add(elt.s)


class Inspector:
    """
    Looks at a file, returns a list of class names that inherit from Workflow class
    """
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
    group = parser.getgroup('joemark')
    group._addoption(
        '--marky-active', action="store_true", dest="active", default=False,
        help='Should the plugin be active'
    )
    group._addoption('--mark-include-marks', dest='marks', nargs='+',
        help='Marks to include. Note this is a list of mark names, not expressions'
    )

    group._addoption('--mark-files', dest='files', nargs='+',
        help='Files to search. If not supplied will look at the latest changes from git.'
    )

    group._addoption('--mark-variable-name', dest='variable', default='PYTEST_MARKS',
        help='Files to search. If not supplied will look at the latest changes from git.'
    )


class MyPlugin:
    def __init__(self, variable, marks=None, files=None):
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

    def pytest_collection_modifyitems(self, session, config, items):
        covered = []
        uncovered = []
        for item in items:
            for m in item.iter_markers():
                if m.name in self._marks:
                    covered.append(item)
                    continue
            uncovered.append(item)
        items[:] = covered
        config.hook.pytest_deselected(items=uncovered)


def pytest_configure(config):
    active = config.getoption("active")
    if active:
        plugin = MyPlugin(
            config.getoption('variable'), marks=config.getoption('marks'), files=config.getoption('files')
        )
        config.pluginmanager.register(plugin, "_filemarker")
