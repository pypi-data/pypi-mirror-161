"""Package for collecting pytest tests."""

import inspect
import pytest


def reindent(string: str) -> str:
    """
    reindent a given code-like string and fix the indentation to have no leading spaces.

    :param string: The string to indent.
    :return: The indented string.
    """

    if not string:
        return string

    # First remove any leading and trailing line drops...
    string = string.strip('\n')

    # Calculate the leading spaces for the first line of the string.
    # ignore '\t' as it isn't common to indent with (and will mess the logic here).
    leading_spaces = len(string) - len(string.lstrip(' '))
    lines = []
    for line in string.splitlines():
        # We use lstrip to remove white spaces at the start of each line,
        # If we will let lstrip work on the whole line it might remove too much...
        # (lets say a double indent for a `for` loop in a function...)
        # So it's only allowed to strip `leading_spaces` at maximum.
        lines.append(line[:leading_spaces].lstrip() + line[leading_spaces:])

    return "\n".join(lines)


class CollectorPlugin:
    """Plugin for pytest that will collect the tests."""

    def __init__(self):
        """
        Create a new collector.
        """

        self._modules = None

    @property
    def modules(self) -> list:
        """
        Get a list of the collected test modules.

        :return: The collected test modules.
        """

        return self._modules

    def pytest_collection_finish(self, session) -> None:
        """
        This is the pytest life-cycle hook that we use to get the collected tests from.
        This hook receives the list of tests via `session.items`.

        :param session: The pytest session data object.
        :return: Nothing (Sets self._modules).
        """

        # First we need to create the tests modules->suites->tests tree.
        modules = {}
        for test in session.items:
            # For each test, traverse up the tree all the way to the root (modules),
            # keeping track of the hierarchy.
            test_module = self.get_test_module_tree(test)
            if test_module["name"] not in modules:
                # If the module is new to us, just save it as a new module.
                modules[test_module["name"]] = test_module
            else:
                # If the current module is already known,
                # we need to merge the new (single) child into the existing module.
                self.merge_child_to_parent(modules[test_module["name"]],
                                           list(test_module["children"].values())[0])

        # Now that we have the tree figured out, we create a list of modules data.
        self._modules = [self.collect_data(module) for module in modules.values()]

    @staticmethod
    def get_test_module_tree(test) -> dict:
        """
        Traverses up the tests hierarchy tree to the modules (root), keeping track of the way up.

        :param test: The test (leaf) to traverse up from.
        :return: The hierarchy from the module (root) to the test (leaf).
        """

        level = test.parent
        hierarchy = {"name": test.name, "obj": test}
        while level.parent is not None:
            hierarchy = {
                "name": level.name,
                "obj": level,
                "children": {hierarchy["name"]: hierarchy}
            }
            level = level.parent

        return hierarchy

    def merge_child_to_parent(self, parent: dict, child: dict) -> None:
        """
        Merge the child into the parent children list.
        if the child already there, recursively makesure the grandchildren are there too.

        :param parent: The parent to add a child to.
        :param child: The child to add.
        :return: Nothing.
        """

        # If the child is new, just add it.
        if child["name"] not in parent["children"]:
            parent["children"][child["name"]] = child
        # If the child is known(not new), go over the grandchildren of the child and add them too.
        elif "children" in child:
            for grandchild in child["children"].values():
                self.merge_child_to_parent(parent["children"][child["name"]], grandchild)

    def collect_data(self, item: dict) -> dict:
        """
        Collects the following data about the given item:
         * type(str) - one of `Module`, `Class`, `Function`.
         * title(str) - the title of the item.
         * doc(str) - the documentation string of the item.
         * src(str) - the source code of the item (for functions only).
         * children(list) - list of children data objects (for non-functions only).

        The children list is collected via recursive call to this function.

        :param item: The item to collect data about.
        :return: The data of the given item.
        """

        # Get the simple data.
        item_obj = item["obj"]
        item_data = {
            "type": type(item_obj).__name__,
            "title": item_obj.name,
            "doc": reindent(item_obj.obj.__doc__),
        }

        # If function get the sources code, if not then collect the children's data.
        if type(item_obj).__name__ == "Function":
            item_data["src"] = reindent(inspect.getsource(item_obj.obj))
        else:
            item_data["children"] = [self.collect_data(child)
                                     for child in item["children"].values()]

        return item_data


def collect(tests_dir_path: str) -> list:
    """
    Collects the test via pytest at the given path.

    NOTE: The pytest tests at the given path will be imported
          by the current process and the fixture will be setup.
          This is so that if there's a repeated test for each of a fixture's outputs,
          that test will be collected as repeated.

    :param tests_dir_path: The path for the tests.
    :return: The collected tests.
    """

    # Create our collector plugin and use pytest with it.
    collector_plugin = CollectorPlugin()
    ret = pytest.main(["--collect-only", "-qq", tests_dir_path], [collector_plugin])
    # ret = pytest.main(["--setup-plan", "-qq", tests_dir], [collector_plugin])

    # Make sure pytest succeeded.
    if ret != pytest.ExitCode.OK:
        raise ValueError(ret)

    # Return the collected test modules.
    return collector_plugin.modules
