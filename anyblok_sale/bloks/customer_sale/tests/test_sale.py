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

    def test_create_customer_sale_order(self):

        # Start with creating a customer
        customer = self.registry.Sale.Customer.create(
                email="john.doe@zeprofile.com", first_name="John",
                last_name="Doe", phone="+33602030405"
                )

        # Then create an address
        address = self.registry.Address.insert(
                first_name=customer.first_name, last_name=customer.last_name,
                street1="1 Esplanade de la défense",
                street2="Grande Arche de la Défense", street3="Paroi Nord",
                zipcode=92800, city="Puteaux", country="FRA",
                state="Ile de France"
                )

        so = self.registry.Sale.Order.create(
                                channel="WEBSITE",
                                code="SO-TEST-000001",
                                customer=customer,
                                customer_address=address,
                                delivery_address=address
                            )
        self.assertEqual(so.state, 'draft')
        self.assertEqual(so.customer, customer)
        self.assertEqual(so.customer_address, address)
        self.assertEqual(so.delivery_address, address)
