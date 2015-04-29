from distutils.core import setup

setup(
    name='ecommerce-api-client',
    version='0.1.0',
    packages=['ecommerce_api_client'],
    url='https://github.com/edx/ecommerce-api-client',
    description='Client used to access edX E-Commerce Service',
    long_description=open('README.rst').read(),
    install_requires=[
        'slumber==0.7.0',
    ],
    tests_require=[
        'coverage==3.7.1',
        'httpretty==0.8.8',
        'nose==1.3.6',
        'pep8==1.6.2',
        'PyJWT==1.1.0',
        'pylint==1.4.3'
    ]
)
