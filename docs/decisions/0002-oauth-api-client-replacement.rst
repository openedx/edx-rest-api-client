2. OAuth API Client replacement
-------------------------------

Status
------

Accepted

Context
-------

The ``EdxRestApiClient`` accepts various types of tokens for authentication, which allows for a wide variety of usages. This means that how authentication is performed is leaked into many different applications and is difficult to standardize and change.

Additionally, ``EdxRestApiClient`` made use of the ``slumber`` python library which is no longer supported.

Decision
--------

We have introduced a new ``OAuthAPIClient`` to replace the now deprecated ``EdxRestApiClient``.  The ``OAuthAPIClient`` can be used for server-to-server calls, accepting a client id and client secret. The underlying implementation of the authentication is meant to be encapsulated and is subject to change.

Because the ``slumber`` python library is no longer supported, it was not used when implementing the ``OAuthAPIClient``.  Instead, the ``OAuthAPIClient`` is now a subclass of the `requests.Session`_ object.

Consequences
------------

All uses of ``EdxRestApiClient`` should ultimately be replaced. Any server-to-server calls can be replaced with ``OAuthAPIClient`` using a client id and client secret.

Other uses and features of ``EdxRestApiClient`` not yet available in ``OAuthAPIClient`` may require additional decisions regarding how and if to replace in such a way that maintains the integrity of this decision to keep the authentication implementation encapsulated inside the client and simpler to update in the future.

Since the ``OAuthAPIClient`` is just a `requests.Session`_ object, its usage and features are well documented.  It is hopefully less likely for this library to go out of support than ``slumber``, and trying to add an abstraction layer to avoid this situation seems like it will add more cost than benefit.

.. _requests.Session: https://requests.readthedocs.io/en/master/user/advanced/#session-objects
