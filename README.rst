edX REST API Client  |CI|_ |Codecov|_
=========================================
.. |CI| image:: https://github.com/edx/edx-rest-api-client/workflows/Python%20CI/badge.svg?branch=master
.. _CI: https://github.com/edx/edx-rest-api-client/actions?query=workflow%3A%22Python+CI%22

.. |Codecov| image:: https://codecov.io/github/edx/edx-rest-api-client/coverage.svg?branch=master
.. _Codecov: https://codecov.io/github/edx/edx-rest-api-client?branch=master

The edX REST API Client (henceforth, client) allows users to communicate with various edX REST APIs, including the `E-Commerce Service`_ and the `Programs Service`_.

.. _E-Commerce Service: https://github.com/edx/ecommerce
.. _Programs Service: https://github.com/edx/programs

Testing
-------
    $ make validate


Clients & REST API Clients code
-------------------------------

Open edX services, including LMS, should use the OAuthAPIClient class to make OAuth2 client requests and REST API calls.

Usage
~~~~~

By default the ``OAuthAPIClient`` object can be used like any `requests.Session`_ object and you can follow the docs that the requests library provides.

The ``OAuthAPIClient`` sessions makes some extra requests to get access tokens from the auth endpoints.  These requests have a default timeout that can be overridden by passing in a ``timeout`` parameter when instantiating the ``OAuthAPIClient`` object.

.. code-block:: python

    # create client with default timeouts for token retrieval
    client = OAuthAPIClient('https://lms.root', 'client_id', 'client_secret')

    # create client, overriding default timeouts for token retrieval
    client = OAuthAPIClient('https://lms.root', 'client_id', 'client_secret', timeout=(6.1, 2))
    client = OAuthAPIClient('https://lms.root', 'client_id', 'client_secret',
         timeout=(REQUEST_CONNECT_TIMEOUT, 3)
    )

    # for a request to some.url, a separate timeout should always be set on your requests
    client.get('https://some.url', timeout=(3.1, 0.5))

The value of the ``timeout`` setting is the same as for any request made with the ``requests`` library.  See the `Requests timeouts documentation`_ for more details.

.. _requests.Session: https://requests.readthedocs.io/en/master/user/advanced/#session-objects
.. _Requests timeouts documentation: https://requests.readthedocs.io/en/master/user/advanced/#timeouts

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
