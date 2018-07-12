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
    """Ensure a tax percentage is always a value between 0 and 1

    :param tax: Tax percentage
    :type tax: int
    :type tax: float
    :type tax: decimal
    :return: A decimal between 0 and 1
    :rtype: decimal

    :Example:

    >>> compute_tax(0.1)
    >>> Decimal('0.1000')
    >>> compute_tax(D('0.1'))
    >>> Decimal('0.1000')
    >>> compute_tax(10)
    >>> Decimal('0.1000')
    >>> compute_tax(D(10))
    >>> Decimal('0.1000')
    """
    if tax != 0:
        if tax > 1 and tax <= 100:
            tax = tax / 100
        elif tax > 0 and tax <= 1:
            tax = tax
        else:
            raise Exception("Tax must be a value between 0 and 1")
    return D(tax).quantize(D('1.0000'))


def compute_price(net=0, gross=0, tax=0, currency='EUR', keep_gross=True):
    """Compute net, gross and tax amount

    The computation can be net or gross based (gross as default)

    :param net: Net price (untaxed)
    :type net: int, float, decimal
    :param gross: Gross price (including taxes)
    :type gross: int, float, decimal
    :param tax: Tax percentage (a value between 0 and 1)
    :type tax: int, float, decimal
    :param currency: Currency (3 character code)
    :type currency: string
    :param keep_gross: A boolean to force computation gross price.
        Default value is True
    :type keep_gross: Boolean
    :return: TaxedMoney from `prices` python package
    :rtype: TaxedMoney

    Example:

    # compute net from gross
    >>> price = compute_price(gross=100, tax=0.2, currency='EUR')
    >>> price
    >>> TaxedMoney(net=Money('83.33', 'EUR'), gross=Money('100.00', 'EUR'))
    >>> price.tax
    >>> Money('16.67', 'EUR')
    # compute gross from net
    >>> price = compute_price(net=83.33, tax=0.2, keep_gross=False)
    >>> price
    >>> TaxedMoney(net=Money('83.33', 'EUR'), gross=Money('100.00', 'EUR'))
    >>> price.tax
    >>> Money('16.67', 'EUR')
    """
    if net != gross:
        if keep_gross:
            net = gross
        else:
            gross = net
    tax = compute_tax(tax)
    return flat_tax(TaxedMoney(
                        Money(D(net), currency).quantize(),
                        Money(D(gross), currency).quantize()),
                    tax,
                    keep_gross=keep_gross)


def compute_discount(price=None, tax=0, discount_amount=0, discount_percent=0,
                     from_gross=True):
    """Apply a discount amount or percent on a price

    The computation can be net or gross based (gross as default)
    If both discount_amount and discount_percent are set, only computation
    on discount_amount will be done

    :param price: Price
    :type price: TaxedMoney
    :param tax: Tax (a value between 0 and 1)
    :type tax: int, float, decimal
    :param discount_amount: Discount amount (Must be a positive value)
    :type discount_amount: int, float, decimal
    :param discount_percent: Discount percent (Must be a value between 0 and 1)
    :type discount_percent: int, float, decimal
    :param from_gross: A boolean to force discount computation on gross price
        Default value is True
    :return: TaxedMoney from `prices` python package
    :rtype: TaxedMoney

    Example:

    >>> price = compute_price(gross=100, tax=0.2, currency='EUR')
    >>> price
    >>> TaxedMoney(net=Money('83.33', 'EUR'), gross=Money('100.00', 'EUR'))
    # Discount amount 10 EUR on gross price
    >>> compute_discount(price=price, tax=0.2, discount_amount=10)
    >>> TaxedMoney(net=Money('75.00', 'EUR'), gross=Money('90.00', 'EUR'))
    # Discount 10% on gross price
    >>> compute_discount(price=price, tax=0.2, discount_percent=0.1)
    >>> TaxedMoney(net=Money('75.00', 'EUR'), gross=Money('90.00', 'EUR'))
    # Discount amount 10 EUR on net price
    >>> compute_discount(
    >>>     price=price, tax=0.2, discount_amount=10, from_gross=False)
    >>> TaxedMoney(net=Money('73.33', 'EUR'), gross=Money('88.00', 'EUR'))
    # Discount 10% on net price
    >>> compute_discount(
    >>>     price=price, tax=0.2, discount_percent=0.1, from_gross=False)
    """
    if price is None:
        return None

    if tax == 0 and price.net.amount != price.gross.amount:
        raise Exception("Tax is set to 0 but gross and net price amount are"
                        " different")

    if discount_amount == 0 and discount_percent == 0:
        return price

    if discount_amount != 0:
        if discount_amount < 0:
            raise Exception("Discount amount must be a positive value")

        discount = fixed_discount(price,
                                  discount=Money(D(discount_amount),
                                                 currency=price.currency)
                                  ).quantize()
        if from_gross:
            return compute_price(gross=discount.gross.amount,
                                 tax=compute_tax(tax),
                                 currency=price.currency,
                                 keep_gross=True)
        else:
            return compute_price(net=discount.net.amount,
                                 tax=compute_tax(tax),
                                 currency=price.currency,
                                 keep_gross=False)

    if discount_percent != 0:
        if discount_percent < 0 or discount_percent > 1:
            raise Exception(
                    "Discount percent must be a value between 0 and 1")

        discount = percentage_discount(price,
                                       percentage=D(discount_percent * 100),
                                       from_gross=from_gross).quantize()

        if from_gross:
            return compute_price(gross=discount.gross.amount,
                                 tax=compute_tax(tax),
                                 currency=price.currency,
                                 keep_gross=True)
        else:
            return compute_price(net=discount.net.amount,
                                 tax=compute_tax(tax),
                                 currency=price.currency,
                                 keep_gross=False)


@Declarations.register(Declarations.Model)
class Sale:
    """Namespace for Sale related models"""
