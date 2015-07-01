import os
import sys
from setuptools import setup, find_packages

_here = os.path.dirname(__file__)

f = open(os.path.join(_here, 'README.md'), 'r')
README = f.read()
f.close()

install_requires = ['lxml', 'PyICU']
if sys.version_info[0] == 2:
    # python2 does not have mock in the standard lib
    install_requires.append('mock')

setup(name="mp.importer",
      version="0.1",
      description="Utilities to ease imports of content to MetroPublisher.",
      packages=find_packages(),
      long_description=README,
      license='BSD',
      author="Vanguardistas LLC",
      author_email='brian@vanguardistas.net',
      install_requires=install_requires,
      include_package_data=True,
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          ],
      test_suite="mp.importer.tests",
      )
