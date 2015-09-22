from setuptools import setup, find_packages


with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='edx-ecommerce-api-client',
    version='1.1.1',
    description='Slumber client used to access APIs exposed by the edX E-Commerce Service',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
    ],
    keywords='edx ecommerce api client',
    url='https://github.com/edx/ecommerce-api-client',
    author='edX',
    author_email='oscm@edx.org',
    license='Apache',
    packages=find_packages(exclude=['*.tests']),
    install_requires=['slumber', 'PyJWT'],
)
