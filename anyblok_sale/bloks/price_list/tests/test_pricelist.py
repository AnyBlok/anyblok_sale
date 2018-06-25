# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-
from decimal import Decimal as D

from sqlalchemy.exc import IntegrityError

from anyblok.tests.testcase import BlokTestCase


class TestPriceListModel(BlokTestCase):
    """ Test price_list model"""

    def test_create_price_list(self):
        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=20,
                    unit_price=69.96
                    )

        self.assertEqual(self.registry.Sale.PriceList.query().count(), 1)
        self.assertEqual(self.registry.Sale.PriceList.Item.query().count(), 1)

    def test_create_price_list_item_ensure_unicity(self):
        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=20,
                    unit_price=69.96
                    )

        with self.assertRaises(IntegrityError) as ctx:
            self.registry.Sale.PriceList.Item.create(
                        price_list=pricelist,
                        item=product,
                        unit_tax=20,
                        unit_price=69.96
                        )
        self.assertTrue(str(ctx.exception.orig).startswith('duplicate key'))

    def test_price_list_item_compute_price_untaxed_from_unit_price(self):
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

    def test_price_list_item_compute_unit_price_from_untaxed(self):
        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")

        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        pli = self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=20,
                    unit_price_untaxed=8.33,
                    keep_gross=False
                    )

        self.assertEqual(pli.unit_price, D('10'))
        self.assertEqual(pli.unit_price_untaxed, D('8.33'))
        self.assertEqual(pli.unit_tax, D('0.2'))

    def test_price_list_item_compute_tax_less_than_1(self):
        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        pli = self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=0.2,
                    unit_price=10
                    )

        self.assertEqual(pli.unit_price, D('10'))
        self.assertEqual(pli.unit_price_untaxed, D('8.33'))
        self.assertEqual(pli.unit_tax, D('0.2'))

    def test_price_list_item_compute_tax_more_than_100(self):
        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        with self.assertRaises(Exception) as ctx:
            self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=120,
                    unit_price=10
                    )

        self.assertTrue(str(ctx.exception).startswith('Tax must be a value'))

    def test_price_list_item_compute_tax_negative(self):
        pricelist = self.registry.Sale.PriceList.create(code="DEFAULT",
                                                        name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        with self.assertRaises(Exception) as ctx:
            self.registry.Sale.PriceList.Item.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=-0.2,
                    unit_price=10
                    )

        self.assertTrue(str(ctx.exception).startswith('Tax must be a value'))
