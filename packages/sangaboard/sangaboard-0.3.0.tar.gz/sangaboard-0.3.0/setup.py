__author__ = 'Bath Open INstrumentation Group'

from setuptools import setup, find_packages
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def find_version():
    """Determine the version based on __init__.py"""
    with open(path.join(here, "sangaboard", "__init__.py"), 'r') as f:
        init_py = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", init_py, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Couldn't parse version string from __init__.py")

version = find_version()

setup(name = 'sangaboard',
      version = version,
      description = 'Communication to the Sangaboard unipolar motor driver',
      long_description = long_description,
      url = 'http://www.gitlab.com/bath_open_instrumentation_group/pysangaboard',
      author = 'Bath Open INstrumentation Group',
      author_email = 'r.w.bowman@bath.ac.uk',
      packages = find_packages(),
      keywords = ['arduino','serial','motor-driver'],
      zip_safe = True,
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7'
          ],
      install_requires = [
          'pyserial',
          'future',
          'numpy',
          'semantic-version',
          ],
      # TODO: add build requires for sphinx, sphinxcontrib-apidoc
      )

