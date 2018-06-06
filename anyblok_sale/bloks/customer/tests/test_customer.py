# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from anyblok.tests.testcase import BlokTestCase
from marshmallow import ValidationError


class TestCustomerModel(BlokTestCase):
    """ Test customer model"""

    def test_create_customer(self):
        self.registry.Customer.create(email="johndoe@sensee.com",
                                      first_name="John",
                                      last_name="Doe",
                                      phone="+33602030405")

        self.assertEqual(self.registry.Customer.query().count(), 1)
        customer = self.registry.Customer.query().first()
        self.assertEqual(customer.email,
                         "johndoe@sensee.com")
        self.assertEqual(str(customer),
                         "John Doe")

    def test_create_customer_fail_required_field(self):
        with self.assertRaises(ValidationError) as ctx:

            self.registry.Customer.create(email="johndoe@sensee.com",
                                          last_name="Doe",
                                          phone="+33602030405")

        self.assertTrue('first_name' in ctx.exception.messages.keys())
        self.assertDictEqual(
            dict(first_name=['Missing data for required field.']),
            ctx.exception.messages)

    def test_create_customer_fail_bad_field(self):
        with self.assertRaises(ValidationError) as ctx:

            self.registry.Customer.create(email="johndoe@sensee.com",
                                          first_name="John",
                                          last_name="Doe",
                                          phone="+33602030405",
                                          unexisting_field="plop")

        self.assertTrue('unexisting_field' in ctx.exception.messages.keys())
        self.assertDictEqual(
            dict(unexisting_field=["Unknown fields {'unexisting_field'} "
                                   "on Model Model.Customer"]),
            ctx.exception.messages)

    def test_create_customer_fail_bad_value(self):
        with self.assertRaises(ValidationError) as ctx:

            self.registry.Customer.create(email="johndoe@sensee.com",
                                          first_name=1337,
                                          last_name="Doe",
                                          phone="+33602030405")

        self.assertDictEqual(
            dict(first_name=['Not a valid string.']),
            ctx.exception.messages)
