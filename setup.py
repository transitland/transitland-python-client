from distutils.core import setup

import onestop

setup(
  name='onestop',
  version=onestop.__version__,
  description='Transitland Onestop',
  author='Ian Rees',
  author_email='ian@mapzen.com',
  url='https://github.com/transitland/onestop-id-python-client',
  license='License :: OSI Approved :: MIT License',
  packages=['onestop'],
  install_requires=['mzgtfs', 'mzgeohash'],
  zip_safe=False,
  # Include examples.
  package_data = {
    '': ['*.txt', '*.md', '*.zip']
  }  
)