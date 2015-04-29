import datetime

import requests
import slumber

from ecommerce_api_client.auth import JwtAuth


class EcommerceApiClient(object):
    """ E-Commerce API client. """

    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, url, signing_key, username, email, timeout=5):
        """ Instantiate a new client. """
        session = requests.Session()
        session.timeout = timeout
        self.api = slumber.API(url, session=session, auth=JwtAuth(username, email, signing_key))

    def _format_order(self, order):
        order['date_placed'] = datetime.datetime.strptime(order['date_placed'], self.DATETIME_FORMAT)
        return order

    def get_order(self, order_number):
        """
        Retrieve a paid order.

        Arguments
            user             --  User associated with the requested order.
            order_number     --  The unique identifier for the order.

        Returns a tuple with the order number, order status, API response data.
        """
        order = self.api.orders(order_number).get()
        self._format_order(order)
        return order

    def get_processors(self):
        """
        Retrieve the list of available payment processors.

        Returns a list of strings.
        """
        return self.api.payment.processors.get()

    def create_basket(self, sku, payment_processor=None):
        """Create a new basket and immediately trigger checkout.

        Note that while the API supports deferring checkout to a separate step,
        as well as adding multiple products to the basket, this client does not
        currently need that capability, so that case is not supported.

        Args:
            user: the django.auth.User for which the basket should be created.
            sku: a string containing the SKU of the course seat being ordered.
            payment_processor: (optional) the name of the payment processor to
                use for checkout.

        Returns:
            A dictionary containing {id, order, payment_data}.

        Raises:
            TimeoutError: the request to the API server timed out.
            InvalidResponseError: the API server response was not understood.
        """
        data = {'products': [{'sku': sku}], 'checkout': True, 'payment_processor_name': payment_processor}
        return self.api.baskets.post(data)

    def get_basket_order(self, basket_id):
        """ Retrieve an order associated with a basket. """
        order = self.api.baskets(basket_id).order.get()
        self._format_order(order)
        return order

    def get_orders(self):
        """ Retrieve all orders for a user. """
        orders = self.api.orders.get()['results']
        orders = [self._format_order(order) for order in orders]
        return orders
