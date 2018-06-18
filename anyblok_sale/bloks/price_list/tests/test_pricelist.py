# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from anyblok.tests.testcase import BlokTestCase


class TestPriceListModel(BlokTestCase):
    """ Test price_list model"""

    def test_create_price_list(self):
        pricelist = self.registry.PriceList.create(code="DEFAULT",
                                                   name="Default")
        product = self.registry.Product.Item.insert(code="TEST",
                                                    name="Test")

        self.registry.PriceListItem.create(
                    price_list=pricelist,
                    item=product,
                    unit_tax=20,
                    unit_price=69.96
                    )

        self.assertEqual(self.registry.PriceList.query().count(), 1)
        self.assertEqual(self.registry.PriceListItem.query().count(), 1)
