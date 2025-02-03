edX REST API Client
###################

| |status-badge| |license-badge| |CI| |Codecov| |pypi-badge|

The edX REST API Client simplifies communicating with other Open edX services by providing OAuth2 and JWT utilities.


Getting Started with Development
********************************

In a Python 3.11 virtual environment:

.. code-block:: shell

    $ make requirements
    $ make validate


Clients & REST API Clients code
*******************************

Open edX services, including LMS, should use the ``OAuthAPIClient`` class to make OAuth2 client requests and REST API calls.

Usage
=====

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
***********************

The OAuthAPIClient uses the TieredCache internally for caching.  Read more about the `requirements of TieredCache`_, which include Django caching and some custom middleware.

.. _requirements of TieredCache: https://github.com/openedx/edx-django-utils/blob/master/edx_django_utils/cache/README.rst#tieredcache

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

More Help
*********

If you're having trouble, we have discussion forums at
`discuss.openedx.org <https://discuss.openedx.org>`_ where you can connect with others in the
community.

Our real-time conversations are on Slack. You can request a `Slack
invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to `open an issue`__ in this
repository with as many details about the issue you are facing as you
can provide.

__ https://github.com/openedx/edx-rest-api-client/issues

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.


.. |CI| image:: https://github.com/openedx/edx-rest-api-client/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/openedx/edx-rest-api-client/actions?query=workflow%3A%22Python+CI%22
    :alt: Test suite status

.. |Codecov| image:: https://codecov.io/github/openedx/edx-rest-api-client/coverage.svg?branch=master
    :target: https://codecov.io/github/openedx/edx-rest-api-client?branch=master
    :alt: Code coverage

.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
    :alt: Maintained

.. |license-badge| image:: https://img.shields.io/github/license/openedx/edx-rest-api-client.svg
    :target: https://github.com/openedx/edx-rest-api-client/blob/master/LICENSE
    :alt: License

.. |pypi-badge| image:: https://img.shields.io/pypi/v/edx-rest-api-client.svg
    :target: https://pypi.python.org/pypi/edx-rest-api-client/
    :alt: PyPI
