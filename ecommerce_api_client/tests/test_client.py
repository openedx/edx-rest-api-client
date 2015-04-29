import json
from unittest import TestCase
from datetime import datetime

import httpretty

from ecommerce_api_client.client import EcommerceApiClient


@httpretty.activate
class EcommerceApiClientTests(TestCase):
    """ Tests for the E-Commerce API client. """
    api_url = 'http://example.com/api/v2'
    date_placed_string = '2015-01-01T00:00:00Z'
    date_placed = datetime.strptime(date_placed_string, EcommerceApiClient.DATETIME_FORMAT)

    def setUp(self):
        super(EcommerceApiClientTests, self).setUp()
        self.client = EcommerceApiClient(self.api_url, 'edx', 'edx', 'edx@example.com')

    def _mock_api_response(self, path, body, method=httpretty.GET):
        url = self.api_url + path
        httpretty.register_uri(method, url, body=json.dumps(body), content_type='application/json')

    def test_get_order(self):
        """ Verify the API retrieves an order. """
        order_number = 'EDX-10001'
        body = {'date_placed': self.date_placed_string}
        self._mock_api_response('/orders/{}/'.format(order_number), body)

        order = self.client.get_order(order_number)
        self.assertEqual(order['date_placed'], self.date_placed)

    def test_get_basket_order(self):
        """ Verify the API retrieves an order associated with a basket. """
        basket_id = '10001'
        body = {'date_placed': self.date_placed_string}
        self._mock_api_response('/baskets/{}/order/'.format(basket_id), body)

        order = self.client.get_basket_order(basket_id)
        self.assertEqual(order['date_placed'], self.date_placed)

    def test_get_orders(self):
        """ Verify the API retrieves a list of orders. """

        body = {'results': [{'date_placed': self.date_placed_string}]}
        self._mock_api_response('/orders/', body)

        orders = self.client.get_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]['date_placed'], self.date_placed)

    def test_get_processors(self):
        """ Verify the API retrieves the list of payment processors. """
        body = ['cybersource', 'paypal']
        self._mock_api_response('/payment/processors/', body)

        processors = self.client.get_processors()
        self.assertEqual(processors, body)

    def test_create_basket(self):
        """ Verify the API creates a new basket. """
        sku = 'test-product'
        payment_processor = 'cybersource'

        self._mock_api_response('/baskets/', {}, httpretty.POST)
        self.client.create_basket(sku, payment_processor)

        request_body = httpretty.last_request().body
        expected = json.dumps(
            {'products': [{'sku': sku}], 'checkout': True, 'payment_processor_name': payment_processor})
        self.assertEqual(request_body, expected)
