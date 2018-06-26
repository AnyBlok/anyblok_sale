# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-
""" PriceList model
"""
from decimal import Decimal as D

from anyblok_marshmallow import ModelSchema

from anyblok import Declarations
from anyblok.column import String, Decimal
from anyblok.relationship import Many2One

from anyblok_sale.bloks.sale_base.base import compute_tax, compute_price


Mixin = Declarations.Mixin


class PriceListItemSchema(ModelSchema):

    class Meta:
        model = "Model.Sale.PriceList.Item"


class PriceListSchema(ModelSchema):

    class Meta:
        model = "Model.Sale.PriceList"


@Declarations.register(Declarations.Model.Sale)
class PriceList(Mixin.UuidColumn, Mixin.TrackModel):

    code = String(label="Code", nullable=False)
    name = String(label="Name", nullable=False)

    def __str__(self):
        return "{self.code} {self.name}".format(self=self)

    def __repr__(self):
        return ("<PriceList(id={self.uuid}, code={self.code}, "
                "name={self.name}>").format(self=self)

    @classmethod
    def create(cls, **kwargs):
        sch = PriceListSchema(registry=cls.registry)
        data = sch.load(kwargs)
        return cls.insert(**data)


@Declarations.register(Declarations.Model.Sale.PriceList)
class Item(Mixin.UuidColumn, Mixin.TrackModel):

    price_list = Many2One(label="Pricelist",
                          model=Declarations.Model.Sale.PriceList,
                          nullable=False,
                          one2many="price_list_items")
    item = Many2One(label="Product Item",
                    model=Declarations.Model.Product.Item,
                    nullable=False,
                    unique=True,
                    one2many="prices")
    unit_price_untaxed = Decimal(label="Price untaxed", default=D(0))
    unit_price = Decimal(label="Price", default=D(0))
    unit_tax = Decimal(label="Tax", default=D(0))

    def __str__(self):
        return "{self.item.code} {self.unit_price_untaxed}".format(self=self)

    def __repr__(self):
        return ("<PriceList(id={self.uuid}, item.code={self.item.code}, "
                "unit_price_untaxed={self.unit_price_untaxed}>").format(
                    self=self)

    @classmethod
    def create(cls, keep_gross=True, **kwargs):
        sch = PriceListItemSchema(registry=cls.registry)
        data = sch.load(kwargs)
        net = data.get('unit_price_untaxed') or D(0)
        gross = data.get('unit_price') or D(0)
        tax = data.get('unit_tax') or D(0)
        price = compute_price(net=net, gross=gross, tax=tax,
                              keep_gross=keep_gross)
        data['unit_price_untaxed'] = price.net.amount
        data['unit_price'] = price.gross.amount
        data['unit_tax'] = compute_tax(tax)
        return cls.insert(**data)
