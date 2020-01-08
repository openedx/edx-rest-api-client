edX REST API Client  |Travis|_ |Codecov|_
=========================================
.. |Travis| image:: https://travis-ci.org/edx/edx-rest-api-client.svg?branch=master
.. _Travis: https://travis-ci.org/edx/edx-rest-api-client

.. |Codecov| image:: https://codecov.io/github/edx/edx-rest-api-client/coverage.svg?branch=master
.. _Codecov: https://codecov.io/github/edx/edx-rest-api-client?branch=master

The edX REST API Client (henceforth, client) allows users to communicate with various edX REST APIs, including the `E-Commerce Service`_ and the `Programs Service`_.

.. _E-Commerce Service: https://github.com/edx/ecommerce
.. _Programs Service: https://github.com/edx/programs

Testing
-------
    $ make validate

Additional Requirements
-----------------------

The OAuthAPIClient uses the TieredCache internally for caching.  Read more about the `requirements of TieredCache`_, which include Django caching and some custom middleware.

.. _requirements of TieredCache: https://github.com/edx/edx-django-utils/blob/master/edx_django_utils/cache/README.rst#tieredcache

How to Contribute
-----------------

Contributions are very welcome, but for legal reasons, you must submit a signed
`individual contributor's agreement`_ before we can accept your contribution. See our
`CONTRIBUTING`_ file for more information -- it also contains guidelines for how to maintain
high code quality, which will make your contribution more likely to be accepted.

.. _individual contributor's agreement: http://code.edx.org/individual-contributor-agreement.pdf
.. _CONTRIBUTING: https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst
