'''setup script for arsenal ansible inventory generator.'''
#  Copyright 2015 CityGrid Media, LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(HERE, 'CHANGELOG.rst')) as f:
    CHANGELOG = f.read()

REQUIRES = [
    'requests',
]

setup(name='rp_arsenal_ansible_inventory',
      version=2.1,
      description='Python script to generate ansbile inventory from an arsenal query.',
      long_description=README + '\n\n' + CHANGELOG,
      classifiers=[
          'Programming Language :: Python',
      ],
      author='Aaron Bandt',
      author_email='abandt@rubiconproject.com',
      url='',
      license='Apache',
      keywords='Arsenal devops',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      tests_require=REQUIRES,
      test_suite='rp_arsenal_ansible_inventory',
      scripts=['bin/arsenal_ansible_inventory.py']
     )
