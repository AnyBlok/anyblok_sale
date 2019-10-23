# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from decimal import Decimal as D
from marshmallow.validate import Length

from anyblok import Declarations
from anyblok.column import String, Decimal, Integer
from anyblok.relationship import Many2One

from anyblok_postgres.column import Jsonb
from anyblok_mixins.workflow.marshmallow import SchemaValidator
from anyblok_marshmallow import fields, SchemaWrapper

from anyblok_sale.bloks.sale_base.base import (
    compute_tax,
    compute_price,
    compute_discount)


Mixin = Declarations.Mixin


class OrderLineBaseSchema(SchemaWrapper):
    model = "Model.Sale.Order.Line"


class OrderBaseSchema(SchemaWrapper):
    model = "Model.Sale.Order"

    class Schema:
        lines = fields.Nested(OrderLineBaseSchema,
                              validate=[Length(min=1)],
                              many=True)


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
                        'price_list']))
            },
            'order': {
                'validators': SchemaValidator(cls.get_schema_definition(
                    exclude=[
                        'price_list']))
            },
            'cancelled': {},
        }

    code = String(label="Code", nullable=False)
    channel = String(label="Sale Channel", nullable=False)
    price_list = Many2One(label="Price list",
                          model=Declarations.Model.Sale.PriceList)
    delivery_method = String(label="Delivery Method")

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
    def create(cls, price_list=None, **kwargs):
        data = kwargs.copy()
        if cls.get_schema_definition:
            sch = cls.get_schema_definition(
                        registry=cls.registry,
                        exclude=['lines']
            )
            if price_list:
                data["price_list"] = price_list.to_primary_keys()
            data = sch.load(data)
            data['price_list'] = price_list

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

    amount_discount_percentage_untaxed = Decimal(
            label="Amount discount percentage untaxed",
            default=D(0))
    amount_discount_percentage = Decimal(label="Amount discount percentage",
                                         default=D(0))
    amount_discount_untaxed = Decimal(label="Amount discount untaxed",
                                      default=D(0))
    amount_discount = Decimal(label="Amount discount", default=D(0))

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
        """

        if not self.order.price_list:
            self.check_unit_price()
            if self.unit_price != D(0) and self.unit_price_untaxed == D(0):
                # compute unit_price_untaxed based on unit_price
                price = compute_price(net=self.unit_price,
                                      gross=self.unit_price,
                                      tax=compute_tax(self.unit_tax),
                                      keep_gross=True)
            elif self.unit_price_untaxed != D(0) and self.unit_price == D(0):
                # compute unit_price based on unit_price_untaxed
                price = compute_price(net=self.unit_price_untaxed,
                                      gross=self.unit_price_untaxed,
                                      tax=compute_tax(self.unit_tax),
                                      keep_gross=False)
            elif self.unit_price_untaxed != D(0) and self.unit_price != D(0):
                # compute unit_price_untaxed based on unit_price
                price = compute_price(net=self.unit_price,
                                      gross=self.unit_price,
                                      tax=compute_tax(self.unit_tax),
                                      keep_gross=True)
            else:
                raise LineException(
                    """Can not find a strategy to compute price"""
                    )

            self.unit_price_untaxed = price.net.amount
            self.unit_price = price.gross.amount
            self.unit_tax = compute_tax(self.unit_tax)
        else:
            # compute unit price based on price list
            price_list_item = self.registry.Sale.PriceList.Item.query(
                    ).filter_by(price_list=self.order.price_list).filter_by(
                            item=self.item).one_or_none()
            if price_list_item:
                self.unit_price = price_list_item.unit_price
                self.unit_price_untaxed = price_list_item.unit_price_untaxed
                self.unit_tax = price_list_item.unit_tax
            else:
                raise LineException(
                    """Can not find a price for %r on %r""" % (
                        self.item, self.order.price_list)
                    )

        # compute total amount
        self.amount_total = D(self.unit_price * self.quantity)
        self.amount_untaxed = D(
                self.unit_price_untaxed * self.quantity)
        self.amount_tax = self.amount_total - self.amount_untaxed

        # compute total amount after discount
        if self.amount_discount_untaxed != D('0'):
            price = compute_price(net=self.amount_untaxed,
                                  tax=self.unit_tax,
                                  keep_gross=False)
            discount = compute_discount(
                        price=price,
                        tax=self.unit_tax,
                        discount_amount=self.amount_discount_untaxed,
                        from_gross=False)

            self.amount_total = discount.gross.amount
            self.amount_untaxed = discount.net.amount
            self.amount_tax = discount.tax.amount
            return

        if self.amount_discount_percentage_untaxed != D('0'):
            price = compute_price(net=self.amount_untaxed,
                                  tax=self.unit_tax,
                                  keep_gross=False)
            discount = compute_discount(
                price=price,
                tax=self.unit_tax,
                discount_percent=self.amount_discount_percentage_untaxed,
                from_gross=False)

            self.amount_total = discount.gross.amount
            self.amount_untaxed = discount.net.amount
            self.amount_tax = discount.tax.amount
            return

        if self.amount_discount != D('0'):
            price = compute_price(gross=self.amount_total,
                                  tax=self.unit_tax,
                                  keep_gross=True)
            discount = compute_discount(
                        price=price,
                        tax=self.unit_tax,
                        discount_amount=self.amount_discount,
                        from_gross=True)
            self.amount_total = discount.gross.amount
            self.amount_untaxed = discount.net.amount
            self.amount_tax = discount.tax.amount
            return

        if self.amount_discount_percentage != D('0'):
            price = compute_price(gross=self.amount_total,
                                  tax=self.unit_tax,
                                  keep_gross=True)
            discount = compute_discount(
                        price=price,
                        tax=self.unit_tax,
                        discount_percent=self.amount_discount_percentage,
                        from_gross=True)

            self.amount_total = discount.gross.amount
            self.amount_untaxed = discount.net.amount
            self.amount_tax = discount.tax.amount
            return

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
