from setuptools import setup

setup(
    name='ecommerce-api-client',
    version='0.4.2',
    packages=['ecommerce_api_client'],
    url='https://github.com/edx/ecommerce-api-client',
    description='Client used to access edX E-Commerce Service',
    long_description=open('README.rst').read(),
    install_requires=[
        # NOTE this version of slumber only exists on the edx fork.
        # dependency_links is deprecated and no longer works, so any packages
        # depending on this package are responsible for manually installing
        # this requirement before this package can be installed.
        'slumber==0.7.1-decode-utf8',
    ],
    tests_require=[
        'coverage==3.7.1',
        'ddt==1.0.0',
        'httpretty==0.8.8',
        'mock==1.0.1',
        'nose==1.3.6',
        'pep8==1.6.2',
        'PyJWT==1.1.0',
        'pylint==1.4.3'
    ]
)
