"""
Flask AppsFoundry
=================

Flask extension library for providing common functionality used by
scoop/appsfoundry Flask-based web applications.
"""
from setuptools import setup, find_packages


pkg_req = [
    'Flask>=0.11.1',
    'Flask-RESTful>=0.3.5',
    'Flask-SQLAlchemy>=2.1',
    'Flask-Babel==0.11.1',

    'SQLAlchemy>=1.1.1',
    'psycopg2>=2.6.2',

    'six==1.10.0',
    'inflect>=0.2.5',
    'requests>=2.11.0',
    'iso3166>=0.7',
    'iso639>=0.1.4',
    'Pillow>=3.3.0',
]
test_req = pkg_req + [
    'fake-factory>=0.4.2',
    'mock>=1.0.1',
    'nose>=1.3.4',
    'coverage>=3.7.1',
    'beautifulsoup4==4.3.2',
]


setup(
    name='Flask-AppsFoundry',
    version='0.1.32',
    url='https://github.com/appsfoundry/scoopflask',
    license='Proprietary',
    author='SCOOP Backend Team',
    author_email='backend@apps-foundry.com',
    description='AppsFoundry utilities for Flask-based applications',
    long_description=__doc__,
    packages=find_packages(exclude=('*.tests.*',)),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=pkg_req,
    tests_require=test_req,
    test_suite='nose.collector'
)
