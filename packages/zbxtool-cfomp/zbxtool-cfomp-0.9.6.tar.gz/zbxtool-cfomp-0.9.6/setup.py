import sys
from setuptools import setup, find_packages
from setuptools.command.test import test

with open("requirements.txt") as reqs_file:
    reqs = reqs_file.readlines()

class PyTest(test):
    def run_tests(self):
        import pytest
        errno = pytest.main()
        sys.exit(errno)


setup(
    name ="zbxtool-cfomp",
    packages = find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires = reqs,
    use_scm_version = {
        "relative_to": __file__,
        "local_scheme": "no-local-version",
    },
    entry_points={
        'console_scripts':[
            'zbxtool = lib.cli:main'
        ],
    },
    setup_requires = ['setuptools_scm==5.0.2']
)
