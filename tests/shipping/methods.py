# -*- coding: utf-8 -*-
from decimal import Decimal as D

from oscar.apps.shipping.methods import Free


class SecondClassRecorded(Free):
    code = 'uk_rm_2ndrecorded'
    name = 'Royal Mail Signed For™ 2nd Class'

    charge_excl_tax = D('0.00')
    charge_incl_tax = D('0.00')
