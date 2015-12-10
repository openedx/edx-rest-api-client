from setuptools import setup, find_packages


with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='edx-rest-api-client',
    version='1.3.0',
    description='Slumber client used to access various edX Platform REST APIs.',
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
    keywords='edx rest api client',
    url='https://github.com/edx/edx-rest-api-client',
    author='edX',
    author_email='oscm@edx.org',
    license='Apache',
    packages=find_packages(exclude=['*.tests']),
    install_requires=['slumber >= 0.7.1, < 1.0', 'PyJWT >= 1.1.0, < 2.0'],
)
