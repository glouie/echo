#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'selenium',
    'beautifulsoup4',
]

test_requirements = [
    # TODO: put package test requirements here
    'selenium',
    'pytest',
]

setup(
    name='echo',
    version='0.0.1',
    description="Foundation libs to build out page objects and models to interact with HTML tags.",
    long_description=readme + '\n\n' + history,
    author="glouie",
    author_email='george.k.louie@gmail.com',
    url='https://github.com/glouie/echo',
    packages=[
        'html',
        'html.util',
        'html.support',
    ],
    package_dir={'html':
                 'html'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT License",
    zip_safe=False,
    keywords='html',
    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
