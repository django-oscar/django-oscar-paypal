from decimal import Decimal as D
from oscar.apps.shipping.methods import Free, FixedPrice
from oscar.apps.shipping.repository import Repository as CoreRepository


class Repository(CoreRepository):

    def get_shipping_methods(self, user, basket, shipping_addr=None, **kwargs):
        methods = [Free(), FixedPrice(D('10.00')), FixedPrice(D('20.00'))]
        return self.add_basket_to_methods(basket, methods)
