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

Mixin = Declarations.Mixin


class PriceListItemSchema(ModelSchema):

    class Meta:
        model = "Model.PriceListItem"


class PriceListSchema(ModelSchema):

    class Meta:
        model = "Model.PriceList"


@Declarations.register(Declarations.Model)
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


@Declarations.register(Declarations.Model)
class PriceListItem(Mixin.UuidColumn, Mixin.TrackModel):

    price_list = Many2One(label="Pricelist",
                          model=Declarations.Model.PriceList,
                          nullable=False,
                          one2many="price_list_items")
    item = Many2One(label="Product Item",
                    model=Declarations.Model.Product.Item,
                    nullable=False,
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
    def create(cls, **kwargs):
        sch = PriceListItemSchema(registry=cls.registry)
        data = sch.load(kwargs)
        return cls.insert(**data)
