# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-
from decimal import Decimal as D
from prices import (
        Money, TaxedMoney, flat_tax, fixed_discount, percentage_discount)

from anyblok import Declarations


def compute_tax(tax=0):
    if tax != 0:
        if tax > 1 and tax <= 100:
            tax = tax / 100
        elif tax > 0 and tax <= 1:
            tax = tax
        else:
            raise Exception("Tax must be a value between 0 and 1")
    return tax


def compute_price(net=0, gross=0, tax=0, currency='EUR', keep_gross=True):
    if net != gross:
        if keep_gross:
            net = gross
        else:
            gross = net
    tax = compute_tax(tax)
    return flat_tax(TaxedMoney(
                        Money(net, currency).quantize(),
                        Money(gross, currency).quantize()),
                    D(tax),
                    keep_gross=keep_gross)


def compute_discount(price=None, discount_amount=0, discount_percent=0):
    if price is None:
        return None
    if discount_amount != 0:
        if discount_amount < 0:
            raise Exception("Discount amount must be a positive value")
        return fixed_discount(price,
                              discount=Money(discount_amount,
                                             currency=price.currency)
                              ).quantize()
    if discount_percent != 0:
        if discount_percent < 0 or discount_percent > 100:
            raise Exception(
                    "Discount percent must be a value between 0 and 100")
        return percentage_discount(price,
                                   percentage=discount_percent).quantize()


@Declarations.register(Declarations.Model)
class Sale:
    """Namespace for Sale related models"""
