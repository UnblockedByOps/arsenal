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

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGELOG.rst')) as f:
    CHANGELOG = f.read()

requires = [
    'pyramid==1.5.1',
    'pyramid_chameleon==0.3',
    'pyramid_debugtoolbar==2.2',
    'pyramid-tm==0.7',
    'pyramid_ldap==0.2',
    'pyramid-mako==1.0.2',
    'Pygments==1.6',
    'waitress==0.8.9',
    'SQLAlchemy==0.9.7',
    'mysql-connector-python==1.2.3',
    'transaction==1.4.3',
    'zope.sqlalchemy==0.7.5',
    'python-ldap==2.4.16',
    'ldappool==1.0',
    'requests==2.3.0',
    'arrow==0.4.4',
    'passlib==1.6.2',
    'PyramidXmlRenderer==0.1.5',
    ]

dependency_links = [
    'https://github.com/CityGrid/pyramid_ldap/tarball/0.2#egg=pyramid_ldap-0.2'
    ]

setup(name='arsenalweb',
      version='0.1',
      description='Arsenal web api/ui',
      long_description=README + '\n\n' + CHANGELOG,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Aaron Bandt',
      author_email='aaron.bandt@citygridmedia.com',
      url='',
      license='Apache',
      keywords='Arsenal devops',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      dependency_links=dependency_links,
      tests_require=requires,
      test_suite="arsenalweb",
      entry_points="""\
      [paste.app_factory]
      main = arsenalweb:main
      [console_scripts]
      initialize_arsenal-web_db = arsenalweb.scripts.initializedb:main
      """,
      )
