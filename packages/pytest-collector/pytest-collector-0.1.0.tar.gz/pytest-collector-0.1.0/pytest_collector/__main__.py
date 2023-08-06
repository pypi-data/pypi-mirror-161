"""Package for collecting pytest tests."""

import sys

import pytest_collector


def main():
    """
    Example executable for collecting pytest.
    Prints the collected tests.

    :return: Nothing
    """

    print(pytest_collector.collect(sys.argv[0]))


if __name__ == '__main__':
    main()
