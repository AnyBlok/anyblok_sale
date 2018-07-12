# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-
""" Customer model
"""
from anyblok_marshmallow import ModelSchema

from anyblok import Declarations
from anyblok.column import String, PhoneNumber, Email

Mixin = Declarations.Mixin


class CustomerSchema(ModelSchema):

    class Meta:
        model = "Model.Sale.Customer"


@Declarations.register(Declarations.Model.Sale)
class Customer(Mixin.UuidColumn, Mixin.TrackModel):

    email = Email(label="Email", unique=True, nullable=False)
    first_name = String(label="First name", nullable=False)
    last_name = String(label="Last name", nullable=False)
    phone = PhoneNumber(label="Main phone number")

    def __str__(self):
        return "{self.first_name} {self.last_name}".format(self=self)

    def __repr__(self):
        return ("<Customer(uuid={self.uuid}, email={self.email}, "
                "first_name={self.first_name},"
                " last_name={self.last_name})>").format(self=self)

    @classmethod
    def create(cls, **kwargs):
        sch = CustomerSchema(registry=cls.registry)
        data = sch.load(kwargs)
        return cls.insert(**data)
