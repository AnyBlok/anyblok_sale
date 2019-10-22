# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from anyblok import Declarations
from anyblok.relationship import Many2One

from anyblok_mixins.workflow.marshmallow import SchemaValidator


Mixin = Declarations.Mixin


@Declarations.register(Declarations.Model.Sale)
class Order:

    """Overrides Sale.Order model in order to add references to customers from
       blok customer from anyblok_sale
    """

    @classmethod
    def get_workflow_definition(cls):

        return {
            'draft': {
                'default': True,
                'allowed_to': ['quotation', 'cancelled']
            },
            'quotation': {
                'allowed_to': ['order', 'cancelled'],
                'validators': SchemaValidator(cls.get_schema_definition(
                    exclude=[
                        'customer',
                        'price_list',
                        'customer_address',
                        'delivery_address']))
            },
            'order': {
                'validators': SchemaValidator(cls.get_schema_definition(
                    exclude=[
                        'customer',
                        'price_list',
                        'customer_address',
                        'delivery_address']))
            },
            'cancelled': {},
        }

    customer = Many2One(label="Customer",
                        model=Declarations.Model.Sale.Customer,
                        one2many='sale_orders')
    customer_address = Many2One(label="Customer Address",
                                model=Declarations.Model.Address)
    delivery_address = Many2One(label="Delivery Address",
                                model=Declarations.Model.Address)

    @classmethod
    def create(cls, price_list=None, **kwargs):
        data = kwargs.copy()
        if cls.get_schema_definition:
            sch = cls.get_schema_definition(
                        registry=cls.registry,
                        exclude=['lines', 'customer', 'customer_address',
                                 'delivery_address']
            )
            if price_list:
                data["price_list"] = price_list.to_primary_keys()
            data = sch.load(data)
            data['price_list'] = price_list

        return cls.insert(**data)
