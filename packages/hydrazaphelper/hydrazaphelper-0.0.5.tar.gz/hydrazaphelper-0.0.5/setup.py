from setuptools import setup, find_packages
import pathlib


VERSION = '0.0.5'
DESCRIPTION = 'Wrapper For OWASP ZAP Application '

# The directory containing this file
HERE = pathlib.Path(__file__).parent

setup(name='hydrazaphelper',
      version='0.0.5',
      description='A small wrapper for owasp zap',
      author='efe.pisirici',
      author_email='efe.pisirici@accenture.com',
      license='Apache',
      setup_requires=['wheel'],
      install_requires=['requests'],
      readme='README.md'
      )