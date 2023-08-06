import os

from setuptools import setup, find_packages

# read the contents of your README file

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

version_dev='1.0.20'
version_prod='1.0.10'

run_mode=''

setup(name='mobio-base-sdk' + run_mode,
      version='1.0.10',
      description='Mobio project SDK',
      url='',
      author='MOBIO',
      author_email='contact@mobio.vn',
      license='MIT',
      package_dir={'': './'},
      packages=find_packages('./'),
      install_requires=['m-singleton',
                        'm-monitor',
                        'm-validator',
                        'Flask>=1.1.2',
                        'flask-cors',
                        'configparser==3.5.0',
                        'logstash_formatter==0.5.17'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      python_requires='>=3.7'
      )
