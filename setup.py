import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open('README.md') as f:
  long_description = f.read()

py_version = sys.version_info[:2]
if py_version < (3, 4):
  raise Exception("asyncio-socketcluster requires Python >= 3.4.")

about = {}
with open(os.path.join(here, 'asyncio_socketcluster', '__version__.py'), 'r') as f:
  exec(f.read(), about)

setup(
  name=about['__title__'],
  version=about['__version__'],
  description=about['__description__'],
  long_description=long_description,
  author=about['__author__'],
  author_email=about['__author_email__'],
  url=about['__url__'],
  license=about['__license__'],
  packages=find_packages(exclude=('tests', 'docs')),
  python_requires='>=3.4',
  install_requires=[
    'websockets'
  ]
)
