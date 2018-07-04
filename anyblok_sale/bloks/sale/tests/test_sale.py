# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from anyblok.tests.testcase import BlokTestCase
from anyblok_mixins.workflow.exceptions import WorkFlowException

from decimal import Decimal as D

from marshmallow.exceptions import ValidationError


class TestSaleOrderModel(BlokTestCase):
    """Test Sale.Order model"""

    def test_create_sale_order(self):
        so = self.registry.Sale.Order.create(
                                channel="WEBSITE",
                                code="SO-TEST-000001"
                            )
        self.assertEqual(so.state, 'draft')

    def test_create_empty_sale_order_fail_validation(self):
        with self.assertRaises(ValidationError) as ctx:
            self.registry.Sale.Order.create()

        self.assertTrue('code' in ctx.exception.messages.keys())
        self.assertEqual(
            ctx.exception.messages.get('code'),
            ['Missing data for required field.']
        )
        self.assertTrue('channel' in ctx.exception.messages.keys())
        self.assertEqual(
            ctx.exception.messages.get('channel'),
            ['Missing data for required field.']
        )

    def test_create_sale_order_fail_validation(self):
        with self.assertRaises(ValidationError) as ctx:
            self.registry.Sale.Order.create(
                                code="SO-TEST-000001"
                            )

        self.assertTrue('channel' in ctx.exception.messages.keys())
        self.assertEqual(
            ctx.exception.messages.get('channel'),
            ['Missing data for required field.']
        )

    def test_sale_order_state_transition_to_quotation_missing_lines(self):
        so = self.registry.Sale.Order.create(
                                channel="WEBSITE",
                                code="SO-TEST-000001"
                            )
        self.assertEqual(so.state, 'draft')

        with self.assertRaises(ValidationError) as ctx:
            so.state_to('quotation')

        self.assertTrue('lines' in ctx.exception.messages.keys())
        self.assertEqual(
            ctx.exception.messages.get('lines'),
            ['Shorter than minimum length 1.']
        )

    def test_sale_order_state_transition_to_done(self):
        so = self.registry.Sale.Order.create(
                                channel="WEBSITE",
                                code="SO-TEST-000001"
                            )

        self.assertEqual(so.state, 'draft')

        product = self.registry.Product.Item.insert(code="TEST", name="Test")
        self.registry.Sale.Order.Line.create(
            order=so,
            item=product,
            quantity=1,
            unit_price=100,
            unit_tax=20
        )

        so.state_to('quotation')
        self.assertEqual(so.state, 'quotation')
        so.state_to('order')
        self.assertEqual(so.state, 'order')

    def test_sale_order_state_transition_to_cancelled(self):
        so = self.registry.Sale.Order.create(
                                channel="WEBSITE",
                                code="SO-TEST-000001"
                            )
        product = self.registry.Product.Item.insert(code="TEST", name="Test")
        self.registry.Sale.Order.Line.create(
            order=so,
            item=product,
            quantity=1,
            unit_price=100,
            unit_tax=20,
        )
        self.assertEqual(so.state, 'draft')
        so.state_to('quotation')
        self.assertEqual(so.state, 'quotation')
        so.state_to('cancelled')
        self.assertEqual(so.state, 'cancelled')

    def test_sale_order_transition_quotation_order_failed(self):
        so = self.registry.Sale.Order.create(
                                channel="WEBSITE",
                                code="SO-TEST-000001"
                            )
        product = self.registry.Product.Item.insert(code="TEST", name="Test")
        self.registry.Sale.Order.Line.create(
            order=so,
            item=product,
            quantity=1,
            unit_price=100,
            unit_tax=20
        )

        so.state_to('quotation')
        so.state_to('order')

        with self.assertRaises(WorkFlowException) as ctx:
            so.state_to('draft')

        self.assertEqual(
            ctx.exception.args[0],
            "No rules found to change state from 'order' to 'draft'")


class TestSaleOrderLineModel(BlokTestCase):
    """Test Sale.Order.Line model"""

    def test_compute_sale_order_line_unit(self):
        so = self.registry.Sale.Order.create(
                     channel="WEBSITE",
                     code="SO-TEST-000001"
                     )

        self.assertEqual(so.state, 'draft')
        product = self.registry.Product.Item.insert(code="TEST", name="test")

        line1 = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=1,
                    unit_price=100,
                    unit_tax=20
                    )

        line2 = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=1,
                    unit_price_untaxed=83.33,
                    unit_tax=20
                    )

        self.assertEqual(line1.unit_price_untaxed, line2.unit_price_untaxed)
        self.assertEqual(line1.unit_price, line2.unit_price)

        self.assertEqual(line1.unit_price_untaxed, line1.amount_untaxed)
        self.assertEqual(line1.unit_price, line1.amount_total)
        self.assertEqual(line1.unit_tax, D('0.2'))

        self.assertEqual(line2.unit_price_untaxed, line2.amount_untaxed)
        self.assertEqual(line2.unit_price, line2.amount_total)
        self.assertEqual(line2.unit_tax, D('0.2'))

        line3 = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=1,
                    unit_price=23.14,
                    unit_tax=2.1
                    )

        line4 = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=1,
                    unit_price_untaxed=22.66,
                    unit_tax=2.1
                    )

        self.assertEqual(line3.unit_price_untaxed, line4.unit_price_untaxed)
        self.assertEqual(line3.unit_price, line4.unit_price)

        self.assertEqual(line3.unit_price_untaxed, line3.amount_untaxed)
        self.assertEqual(line3.unit_price, line3.amount_total)
        self.assertEqual(line3.unit_tax, D('0.021'))

        self.assertEqual(line4.unit_price_untaxed, line4.amount_untaxed)
        self.assertEqual(line4.unit_price, line4.amount_total)
        self.assertEqual(line4.unit_tax, D('0.021'))

        line5 = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=1,
                    unit_price=100,
                    unit_price_untaxed=83.33,
                    unit_tax=20
                    )

        self.assertEqual(line5.unit_price_untaxed, D('83.33'))
        self.assertEqual(line5.unit_price_untaxed, line5.amount_untaxed)
        self.assertEqual(line5.unit_price, line5.amount_total)
        self.assertEqual(line5.unit_tax, D('0.2'))

        self.assertEqual(so.amount_untaxed, D('0'))
        self.assertEqual(so.amount_tax, D('0'))
        self.assertEqual(so.amount_total, D('0'))
        so.compute()
        self.assertEqual(so.amount_untaxed, D('295.31'))
        self.assertEqual(so.amount_tax, D('50.97'))
        self.assertEqual(so.amount_total, D('346.28'))

    def test_compute_sale_order_line_product_price_list(self):

        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        pli = self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=20,
                    unit_price=10
                    )
        self.assertEqual(pli.unit_price, D('10'))
        self.assertEqual(pli.unit_price_untaxed, D('8.33'))
        self.assertEqual(pli.unit_tax, D('0.2'))

        so = self.registry.Sale.Order.create(
                     channel="WEBSITE",
                     price_list=pricelist,
                     code="SO-TEST-000001"
                     )
        self.assertEqual(so.price_list, pricelist)

        line1 = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=1
                    )

        self.assertEqual(line1.unit_price, D('10'))
        self.assertEqual(line1.unit_price_untaxed, D('8.33'))
        self.assertEqual(line1.unit_tax, D('0.2'))

        self.assertEqual(line1.amount_untaxed, D('8.33'))
        self.assertEqual(line1.amount_tax, D('1.67'))
        self.assertEqual(line1.amount_total, D('10'))

        self.assertEqual(so.amount_untaxed, D('0'))
        self.assertEqual(so.amount_tax, D('0'))
        self.assertEqual(so.amount_total, D('0'))

        so.compute()
        self.assertEqual(so.amount_untaxed, D('8.33'))
        self.assertEqual(so.amount_tax, D('1.67'))
        self.assertEqual(so.amount_total, D('10'))

    def test_compute_sale_order_line_total_quantity(self):
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")
        so = self.registry.Sale.Order.create(
                     channel="WEBSITE",
                     code="SO-TEST-000001"
                     )
        line = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=2,
                    unit_price_untaxed=83.33,
                    unit_tax=20
                    )

        self.assertEqual(line.unit_price, D('100'))
        self.assertEqual(line.unit_price_untaxed, D('83.33'))
        self.assertEqual(line.unit_tax, D('0.2'))

        self.assertEqual(line.amount_untaxed, D('166.66'))
        self.assertEqual(line.amount_tax, D('33.34'))
        self.assertEqual(line.amount_total, D('200'))

        so.compute()
        self.assertEqual(so.amount_untaxed, D('166.66'))
        self.assertEqual(so.amount_tax, D('33.34'))
        self.assertEqual(so.amount_total, D('200'))

    def test_compute_sale_order_line_total_quantity_with_pricelist(self):

        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        pli = self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=20,
                    unit_price=10
                    )
        self.assertEqual(pli.unit_price, D('10'))
        self.assertEqual(pli.unit_price_untaxed, D('8.33'))
        self.assertEqual(pli.unit_tax, D('0.2'))

        so = self.registry.Sale.Order.create(
                     channel="WEBSITE",
                     price_list=pricelist,
                     code="SO-TEST-000002"
                     )
        self.assertEqual(so.price_list, pricelist)

        line = self.registry.Sale.Order.Line.create(
                    order=so,
                    item=product,
                    quantity=2
                    )

        self.assertEqual(line.unit_price, D('10'))
        self.assertEqual(line.unit_price_untaxed, D('8.33'))
        self.assertEqual(line.unit_tax, D('0.2'))

        self.assertEqual(line.amount_untaxed, D('16.66'))
        self.assertEqual(line.amount_tax, D('3.34'))
        self.assertEqual(line.amount_total, D('20'))

        self.assertEqual(so.amount_untaxed, D('0'))
        self.assertEqual(so.amount_tax, D('0'))
        self.assertEqual(so.amount_total, D('0'))

        so.compute()
        self.assertEqual(so.amount_untaxed, D('16.66'))
        self.assertEqual(so.amount_tax, D('3.34'))
        self.assertEqual(so.amount_total, D('20'))
