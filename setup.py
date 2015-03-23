from distutils.core import setup

import onestop

setup(
  name='onestop',
  version=onestop.__version__,
  description='Transitland Onestop',
  author='Ian Rees',
  author_email='ian@mapzen.com',
  url='http://mapzen.com/',
  license='License :: OSI Approved :: MIT License',
  packages=['onestop']
)