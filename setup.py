#!/usr/bin/env python
""" Setup to allow pip installs of edx-rest-api-client module """

from setuptools import setup, find_packages

from edx_rest_api_client import __version__

with open('README.rst') as readme:
    long_description = readme.read()


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.
    Returns a list of requirement strings.
    """
    requirements = set()
    for path in requirements_paths:
        with open(path) as reqs:
            requirements.update(
                line.split('#')[0].strip() for line in reqs
                if is_requirement(line.strip())
            )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement;
    that is, it is not blank, a comment, a URL, or an included file.
    """
    return line and not line.startswith(('-r', '#', '-e', 'git+', '-c'))


setup(
    name='edx-rest-api-client',
    version=__version__,
    description='Slumber client used to access various edX Platform REST APIs.',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Topic :: Internet',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
    ],
    keywords='edx rest api client',
    url='https://github.com/edx/edx-rest-api-client',
    author='edX',
    author_email='oscm@edx.org',
    license='Apache',
    packages=find_packages(exclude=['*.tests']),
    install_requires=load_requirements('requirements/base.in'),
)
