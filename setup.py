from setuptools import setup

import transitland

setup(
  name='transitland',
  version=transitland.__version__,
  description='Transitland Client',
  author='Ian Rees',
  author_email='ian@mapzen.com',
  url='https://github.com/transitland/transitland-python-client',
  license='License :: OSI Approved :: MIT License',
  packages=['transitland'],
  install_requires=[
    'mzgtfs>=0.10.0', 
    'mzgeohash'
  ],
  zip_safe=False,
  # Include examples.
  package_data = {
    '': ['*.txt', '*.md', '*.zip', '*.json', '*.geojson']
  }  
)