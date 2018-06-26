# This file is a part of the AnyBlok / Sale project
#
#    Copyright (C) 2018 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
# -*- coding: utf-8 -*-

from anyblok.blok import Blok
from logging import getLogger
logger = getLogger(__name__)


class SaleBaseBlok(Blok):
    """SaleBase blok
    Mainly used to get a `Sale` namespace
    """
    version = "0.1.0"
    author = "Franck BRET"

    required = ['anyblok-core']

    @classmethod
    def import_declaration_module(cls):
        from . import base # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import base
        reload(base)
