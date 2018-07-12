# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from anyblok.tests.testcase import BlokTestCase

from decimal import Decimal as D

from anyblok_sale.bloks.sale_base.base import (
            compute_tax, compute_price, compute_discount)


class TestSaleBase(BlokTestCase):

    def test_compute_tax(self):
        tax = compute_tax(20)
        self.assertEqual(tax, D('0.2000'))
        tax = compute_tax(D(20))
        self.assertEqual(tax, D('0.2000'))

        tax = compute_tax(0.2)
        self.assertEqual(tax, D('0.2000'))

        tax = compute_tax(D(0.2))
        self.assertEqual(tax, D('0.2000'))

        tax = compute_tax(0.22)
        self.assertEqual(tax, D('0.2200'))

        tax = compute_tax(0.222222)
        self.assertEqual(tax, D('0.2222'))

    def test_compute_tax_exception(self):
        with self.assertRaises(Exception) as ctx:
            compute_tax(-0.2)
        self.assertEqual(str(ctx.exception),
                         "Tax must be a value between 0 and 1")

        with self.assertRaises(Exception) as ctx:
            compute_tax(200)
        self.assertEqual(str(ctx.exception),
                         "Tax must be a value between 0 and 1")

    def test_compute_price_from_net_no_tax(self):
        price = compute_price(net=100, keep_gross=False)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D(0))

    def test_compute_price_from_gross_no_tax(self):
        price = compute_price(gross=100, keep_gross=True)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D(0))

    def test_compute_price_from_net(self):
        price = compute_price(net=0.97, tax=0.021, keep_gross=False)
        self.assertEqual(price.net.amount, D('0.97'))
        self.assertEqual(price.gross.amount, D('0.99'))
        self.assertEqual(price.tax.amount, D('0.02'))

        price = compute_price(net=83.33, tax=0.2, keep_gross=False)
        self.assertEqual(price.net.amount, D('83.33'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D('16.67'))

        price = compute_price(net=8361.20, tax=0.196, keep_gross=False)
        self.assertEqual(price.net.amount, D('8361.20'))
        self.assertEqual(price.gross.amount, D('10000'))
        self.assertEqual(price.tax.amount, D('1638.80'))

    def test_compute_price_from_gross(self):
        price = compute_price(gross=0.99, tax=0.021, keep_gross=True)
        self.assertEqual(price.net.amount, D('0.97'))
        self.assertEqual(price.gross.amount, D('0.99'))
        self.assertEqual(price.tax.amount, D('0.02'))

        price = compute_price(gross=100, tax=0.2, keep_gross=True)
        self.assertEqual(price.net.amount, D('83.33'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D('16.67'))

        price = compute_price(gross=10000, tax=0.196, keep_gross=True)
        self.assertEqual(price.net.amount, D('8361.20'))
        self.assertEqual(price.gross.amount, D('10000'))
        self.assertEqual(price.tax.amount, D('1638.80'))

    def test_compute_price_from_net_no_tax_fixed_discount(self):
        price = compute_price(net=100, keep_gross=False)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D(0))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price, discount_amount=9.99,
                                    from_gross=False)
        self.assertEqual(discount.net.amount, D('90.01'))
        self.assertEqual(discount.gross.amount, D('90.01'))
        self.assertEqual(discount.tax.amount, D(0))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_net_no_tax_percentage_discount(self):
        price = compute_price(net=100, keep_gross=False)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D(0))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    discount_percent=0.1,
                                    from_gross=False)
        self.assertEqual(discount.net.amount, D('90'))
        self.assertEqual(discount.gross.amount, D('90'))
        self.assertEqual(discount.tax.amount, D(0))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_net_no_tax_fixed_and_percentage_discount(self):
        price = compute_price(net=100, keep_gross=False)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D(0))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    discount_amount=9.99,
                                    discount_percent=0.1,
                                    from_gross=False)
        # for now only discount_amount is applied if both discount_amount and
        # discount_percent are set
        self.assertEqual(discount.net.amount, D('90.01'))
        self.assertEqual(discount.gross.amount, D('90.01'))
        self.assertEqual(discount.tax.amount, D(0))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_discount_exception(self):
        self.assertEqual(compute_discount(discount_amount=1), None)

        price = compute_price(net=100, keep_gross=False)

        with self.assertRaises(Exception) as ctx:
            compute_discount(price=price, discount_percent=-10)
        self.assertEqual(str(ctx.exception),
                         "Discount percent must be a value between 0 and 1")

        with self.assertRaises(Exception) as ctx:
            compute_discount(price=price, discount_percent=200)
        self.assertEqual(str(ctx.exception),
                         "Discount percent must be a value between 0 and 1")

    def test_compute_price_from_net_fixed_discount(self):
        price = compute_price(net=100, tax=0.2, keep_gross=False)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('120'))
        self.assertEqual(price.tax.amount, D('20'))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    tax=0.2,
                                    discount_amount=10,
                                    from_gross=False)

        self.assertEqual(discount.net.amount, D('90'))
        self.assertEqual(discount.gross.amount, D('108'))
        self.assertEqual(discount.tax.amount, D('18'))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_net_percentage_discount(self):
        price = compute_price(net=100, tax=0.2, keep_gross=False)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('120'))
        self.assertEqual(price.tax.amount, D('20'))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    tax=0.2,
                                    discount_percent=0.1,
                                    from_gross=False
                                    )
        self.assertEqual(discount.net.amount, D('90'))
        self.assertEqual(discount.gross.amount, D('108'))
        self.assertEqual(discount.tax.amount, D('18'))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_net_fixed_and_percentage_discount(self):
        price = compute_price(net=83.33, tax=0.2, keep_gross=False)
        self.assertEqual(price.net.amount, D('83.33'))
        self.assertEqual(price.gross.amount, D('100'))
        self.assertEqual(price.tax.amount, D('16.67'))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    tax=0.2,
                                    discount_amount=9.99,
                                    discount_percent=0.1,
                                    from_gross=False)
        # for now only discount_amount is applied if both discount_amount and
        # discount_percent are set
        self.assertEqual(discount.net.amount, D('73.34'))
        self.assertEqual(discount.gross.amount, D('88.01'))
        self.assertEqual(discount.tax.amount, D('14.67'))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_gross_fixed_discount(self):
        price = compute_price(gross=120, tax=0.2, keep_gross=True)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('120'))
        self.assertEqual(price.tax.amount, D('20'))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    tax=0.2,
                                    discount_amount=10,
                                    from_gross=True)

        self.assertEqual(discount.net.amount, D('91.67'))
        self.assertEqual(discount.gross.amount, D('110'))
        self.assertEqual(discount.tax.amount, D('18.33'))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_gross_percentage_discount(self):
        price = compute_price(gross=120, tax=0.2, keep_gross=True)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('120'))
        self.assertEqual(price.tax.amount, D('20'))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    tax=0.2,
                                    discount_percent=0.1,
                                    from_gross=True
                                    )
        self.assertEqual(discount.net.amount, D('90'))
        self.assertEqual(discount.gross.amount, D('108'))
        self.assertEqual(discount.tax.amount, D('18'))
        self.assertEqual(discount.currency, 'EUR')

    def test_compute_price_from_gross_fixed_and_percentage_discount(self):
        price = compute_price(gross=120, tax=0.2, keep_gross=True)
        self.assertEqual(price.net.amount, D('100'))
        self.assertEqual(price.gross.amount, D('120'))
        self.assertEqual(price.tax.amount, D('20'))
        self.assertEqual(price.currency, 'EUR')

        discount = compute_discount(price=price,
                                    tax=0.2,
                                    discount_amount=10,
                                    discount_percent=0.1,
                                    from_gross=True)
        # for now only discount_amount is applied if both discount_amount and
        # discount_percent are set
        self.assertEqual(discount.net.amount, D('91.67'))
        self.assertEqual(discount.gross.amount, D('110'))
        self.assertEqual(discount.tax.amount, D('18.33'))
        self.assertEqual(discount.currency, 'EUR')
