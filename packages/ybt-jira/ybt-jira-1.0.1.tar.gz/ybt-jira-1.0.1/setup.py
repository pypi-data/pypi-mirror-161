# this file is added to workaround the the error message
# saying “Project file has a ‘pyproject.toml’ and its build
# backend is missing the ‘build_editable’ hook.” when running
# python -m pip install -e .
# This is due to a limitation in Setuptools support for PEP 660.

from setuptools import setup

setup()
