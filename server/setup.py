'''setup script for arsenal web.'''
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
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'Chameleon==3.9.0',
    'Mako==1.2.2',
    'MarkupSafe==2.0.0',
    'PasteDeploy==2.1.1',
    'Pygments==2.15.0',
    'SQLAlchemy==1.4.15',
    'WebOb==1.8.7',
    'WebTest==2.0.35',
    'attrs==21.2.0',
    'beautifulsoup4==4.9.3',
    'certifi==2023.7.22',
    'chardet==4.0.0',
    'coverage==5.5',
    'greenlet==1.1.0',
    'hupper==1.10.2',
    'idna==2.10',
    'importlib-metadata==4.0.1',
    'iniconfig==1.1.1',
    'mysqlclient==2.2.4',
    'packaging==20.9',
    'pam==0.2.0',
    'passlib==1.7.4',
    'plaster-pastedeploy==0.7',
    'plaster==1.0',
    'pluggy==0.13.1',
    'py==1.10.0',
    'pyparsing==2.4.7',
    'pyramid-chameleon==0.3',
    'pyramid-debugtoolbar==4.9',
    'pyramid-mako==1.1.0',
    'pyramid-retry==2.1.1',
    'pyramid-tm==2.4',
    'pyramid==2.0.2',
    'pytest-cov==2.11.1',
    'pytest==6.2.4',
    'python-dateutil==2.8.1',
    'python-editor==1.0.4',
    'python-pam==1.8.4',
    'pytz==2021.1',
    'repoze.lru==0.7',
    'requests==2.31.0',
    'six==1.16.0',
    'soupsieve==2.2.1',
    'toml==0.10.2',
    'transaction==3.0.1',
    'translationstring==1.4',
    'typing-extensions==3.10.0.0',
    'urllib3==1.26.5',
    'venusian==3.0.0',
    'waitress==2.1.2',
    'wheel==0.38.1',
    'zipp==3.4.1',
    'zope.deprecation==4.4.0',
    'zope.interface==5.4.0',
    'zope.sqlalchemy==1.4',
]

tests_require = [
    'WebTest',
    'pytest',
    'pytest-cov',
]

setup(
    name='arsenalweb',
    version='12.7.0',
    description='Arsenal web api/ui',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Aaron Bandt',
    author_email='abandt@magnite.com',
    url='ihttps://github.com/UnblockedByOps/arsenal',
    license='Apache',
    keywords='Arsenal devops web pyramid pylons',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = arsenalweb:main',
        ],
        'console_scripts': [
            'initialize_arsenalweb_db=arsenalweb.scripts.initialize_db:main',
        ],
    },
)
