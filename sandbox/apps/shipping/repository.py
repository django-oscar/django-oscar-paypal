from decimal import Decimal as D

from oscar.apps.shipping.methods import Free, FixedPrice
from oscar.apps.shipping.repository import Repository as CoreRepository


class Repository(CoreRepository):
    """
    This class is included so that there is a choice of shipping methods.
    Oscar's default behaviour is to only have one which means you can't test
    the shipping features of PayPal.
    """
    methods = [Free(), FixedPrice(D('10.00'), D('10.00'))]
