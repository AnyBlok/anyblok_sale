# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from decimal import Decimal as D

from anyblok import Declarations
from anyblok.column import String, Decimal, Integer
from anyblok.relationship import Many2One

from anyblok_postgres.column import Jsonb
from anyblok_mixins.workflow.marshmallow import SchemaValidator
from anyblok_marshmallow import fields, ModelSchema

from marshmallow.validate import Length


Mixin = Declarations.Mixin


class OrderLineBaseSchema(ModelSchema):

    class Meta:
        model = "Model.Sale.Order.Line"


class OrderBaseSchema(ModelSchema):
    lines = fields.Nested(OrderLineBaseSchema,
                          validate=[Length(min=1)],
                          many=True)

    class Meta:
        model = "Model.Sale.Order"


@Declarations.register(Declarations.Model)
class Sale:
    """Namespace for Sale related models"""


class LineException(Exception):
    pass


@Declarations.register(Declarations.Model.Sale)
class Order(Mixin.UuidColumn, Mixin.TrackModel, Mixin.WorkFlow):
    """Sale.Order model
    """
    SCHEMA = OrderBaseSchema

    @classmethod
    def get_schema_definition(cls, **kwargs):
        return cls.SCHEMA(**kwargs)

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
                        'customer_address',
                        'delivery_address']))
            },
            'order': {
                'validators': SchemaValidator(cls.get_schema_definition(
                    exclude=[
                        'customer',
                        'customer_address',
                        'delivery_address']))
            },
            'cancelled': {},
        }

    code = String(label="Code", nullable=False)
    channel = String(label="Sale Channel", nullable=False)
    delivery_method = String(label="Delivery Method")

    customer = Many2One(label="Customer",
                        model=Declarations.Model.Customer,
                        one2many='sale_orders')
    customer_address = Many2One(label="Customer Address",
                                model=Declarations.Model.Address)
    delivery_address = Many2One(label="Delivery Address",
                                model=Declarations.Model.Address)

    amount_untaxed = Decimal(label="Amount Untaxed", default=D(0))
    amount_tax = Decimal(label="Tax amount", default=D(0))
    amount_total = Decimal(label="Total", default=D(0))

    def __str__(self):
        return "{self.uuid} {self.channel} {self.code} {self.state}".format(
            self=self)

    def __repr__(self):
        return "<Sale(id={self.uuid}, code={self.code}," \
               " amount_untaxed={self.amount_untaxed},"\
               " amount_tax={self.amount_tax},"\
               " amount_total={self.amount_total},"\
               " channel={self.channel} state={self.state})>".format(
                    self=self)

    @classmethod
    def create(cls, **kwargs):
        if cls.get_schema_definition:
            sch = cls.get_schema_definition(
                        registry=cls.registry,
                        exclude=['lines', 'customer', 'customer_address',
                                 'delivery_address']
            )
            data = sch.load(kwargs)
        else:
            data = kwargs
        return cls.insert(**data)

    def compute(self):
        """Compute order total amount"""
        amount_untaxed = D(0)
        amount_tax = D(0)
        amount_total = D(0)

        for line in self.lines:
            amount_untaxed += line.amount_untaxed
            amount_tax += line.amount_tax
            amount_total += line.amount_total

        self.amount_untaxed = amount_untaxed
        self.amount_tax = amount_tax
        self.amount_total = amount_total


@Declarations.register(Declarations.Model.Sale.Order)
class Line(Mixin.UuidColumn, Mixin.TrackModel):
    """Sale.Order.Line Model
    """
    SCHEMA = OrderLineBaseSchema

    @classmethod
    def get_schema_definition(cls, **kwargs):
        return cls.SCHEMA(**kwargs)

    order = Many2One(label="Order",
                     model=Declarations.Model.Sale.Order,
                     nullable=False,
                     one2many="lines")

    item = Many2One(label="Product Item",
                    model=Declarations.Model.Product.Item,
                    nullable=False)

    properties = Jsonb(label="Item properties", default=dict())

    unit_price_untaxed = Decimal(label="Price untaxed", default=D(0))
    unit_price = Decimal(label="Price", default=D(0))
    unit_tax = Decimal(label="Tax", default=D(0))

    quantity = Integer(label="Quantity", default=1, nullable=False)

    amount_untaxed = Decimal(label="Amount untaxed", default=D(0))
    amount_tax = Decimal(label="Tax amount", default=D(0))
    amount_total = Decimal(label="Total", default=D(0))

    def __str__(self):
        return "{self.uuid} : {self.amount_total}".format(self=self)

    def __repr__(self):
        return "<Sale.Order.Line(uuid={self.uuid},"\
               " amount_untaxed={self.amount_untaxed},"\
               " amount_tax={self.amount_tax},"\
               " amount_total={self.amount_total})>".format(self=self)

    def check_unit_price(self):
        """Ensure consistency between unit_price_untaxed, unit_price and
        unit_tax
        TODO: Move this to a specialized marshmallow validation method
        """
        if (self.unit_price_untaxed < D(0) or
                self.unit_price < D(0) or self.unit_tax < D(0)):
            raise LineException(
                """Negative Value forbidden on unit_price_untaxed, unit_price
                or unit_tax"""
                )

        if (self.unit_price_untaxed != self.unit_price and
                self.unit_tax == D(0)):
            raise LineException(
                """Inconsistency between unit_price_untaxed, unit_price
                and unit_tax"""
                )

        if self.unit_tax != D(0):
            if (self.unit_price_untaxed >= self.unit_price and
                    self.unit_price != D(0)):
                raise LineException(
                    """unit_price_untaxed can not be greater than unit_price"""
                    )

    def compute(self):
        """Compute order line total amount

        * check unit_price consistency
        * compute tax if any
        * compute line total amount

        TODO: maybe add configuration options for computation behaviours, for
        example computation based on unit_price or unit_price_untaxed

        TODO: Maybe use 'Prices' module for decimal conversion and currency
        management
        """
        self.check_unit_price()

        unit_price_untaxed = D(self.unit_price_untaxed).quantize(D('1.0000'))
        unit_price = D(self.unit_price).quantize(D('1.0000'))

        if self.unit_tax != D(0):
            tax = D(D(self.unit_tax / 100).quantize(D('1.0000'))) + 1

            if self.unit_price != D(0) and self.unit_price_untaxed == D(0):
                # compute unit_price_untaxed based on unit_price
                self.unit_price_untaxed = D(unit_price / tax).quantize(
                        D('1.00'))
                self.unit_price = unit_price
            elif self.unit_price_untaxed != D(0) and self.unit_price == D(0):
                # compute unit_price based on unit_price_untaxed
                self.unit_price = D(unit_price_untaxed * tax).quantize(
                        D('1.00'))
                self.unit_price_untaxed = unit_price_untaxed
            elif self.unit_price_untaxed != D(0) and self.unit_price != D(0):
                # compute unit_price_untaxed based on unit_price
                self.unit_price_untaxed = D(unit_price / tax).quantize(
                        D('1.00'))
                self.unit_price = unit_price
            else:
                pass

        # compute total
        self.amount_total = D(self.unit_price * self.quantity).quantize(
                D('1.00'))
        self.amount_untaxed = D(
                self.unit_price_untaxed * self.quantity).quantize(D('1.00'))
        self.amount_tax = self.amount_total - self.amount_untaxed

    @classmethod
    def create(cls, order=None, item=None, **kwargs):
        data = kwargs.copy()

        if order is None:
            raise TypeError

        if item is None:
            raise TypeError

        if cls.get_schema_definition:
            sch = cls.get_schema_definition(
                        registry=cls.registry,
                        required_fields=["order", "item", "quantity"]
            )
            data['item'] = item.to_primary_keys()
            data['order'] = order.to_primary_keys()

            data = sch.load(data)

            data['item'] = item
            data['order'] = order

        line = cls.insert(**data)
        line.compute()
        return line

    @classmethod
    def before_update_orm_event(cls, mapper, connection, target):
        if cls.get_schema_definition:
            sch = cls.get_schema_definition(
                        registry=cls.registry,
                        required_fields=["order", "item", "quantity"]
            )

            sch.load(sch.dump(target))

            if (target.properties and
                cls.registry.System.Blok.is_installed('product_family') and
                    target.item.template.family.custom_schemas):
                props = target.item.template.family.custom_schemas.get(
                            target.item.code.lower()).get('schema')
                props_sch = props(context={"registry": cls.registry})
                props_sch.load(target.properties)

        target.compute()
