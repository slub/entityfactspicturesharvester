"""
A commandline command (Python3 program) that reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves and stores the pictures and thumbnails contained in this information.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='entityfactspicturesharvester',
      version='0.0.1',
      description='a commandline command (Python3 program) that reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves and stores the pictures and thumbnails contained in this information',
      url='https://github.com/slub/entityfactspicturesharvester',
      author='Bo Ferri',
      author_email='zazi@smiy.org',
      license="Apache 2.0",
      packages=[
          'entityfactspicturesharvester',
      ],
      package_dir={'entityfactspicturesharvester': 'entityfactspicturesharvester'},
      install_requires=[
          'argparse>=1.4.0',
          'requests>=2.22.0',
          'rx>=3.0.1'
      ],
      entry_points={
          "console_scripts": ["entityfactspicturesharvester=entityfactspicturesharvester.entityfactspicturesharvester:run"]
      }
      )
