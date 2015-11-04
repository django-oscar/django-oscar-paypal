# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal as D

from oscar.apps.shipping.methods import Free


class Oscar07Mixin(object):
    """
    for Oscar 0.7 compatibility
    (different shipping method api)
    """
    def __call__(self):
        return self

    def set_basket(self, basket):
        pass


class SecondClassRecorded(Oscar07Mixin, Free):
    code = 'uk_rm_2ndrecorded'
    name = 'Royal Mail Signed For™ 2nd Class'

    charge_excl_tax = D('0.00')
    charge_incl_tax = D('0.00')
