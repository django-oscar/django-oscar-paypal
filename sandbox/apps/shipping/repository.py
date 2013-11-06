from decimal import Decimal as D

from oscar.apps.shipping.methods import Free, FixedPrice
from oscar.apps.shipping.repository import Repository as CoreRepository


class Repository(CoreRepository):
    """
    This class is included so that there is a choice of shipping methods.
    Oscar's default behaviour is to only have one which means you can't test
    the shipping features of PayPal.
    """
    methods = [Free(), FixedPrice(D('10.00'))]

    def get_shipping_methods(self, user, basket, shipping_addr=None, **kwargs):
        return self.prime_methods(basket, self.methods)

    def find_by_code(self, code, basket):
        for method in self.methods:
            if code == method.code:
                return self.prime_method(basket, method)
