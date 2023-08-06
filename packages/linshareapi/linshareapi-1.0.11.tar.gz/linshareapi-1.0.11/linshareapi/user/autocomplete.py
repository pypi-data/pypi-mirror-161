
#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


# This file is part of Linshare api.
#
# LinShare api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2020 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#




import urllib.request, urllib.parse, urllib.error

from linshareapi.core import ResourceBuilder
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.user.core import GenericClass
from linshareapi.user.core import Time as CTime
from linshareapi.user.core import CM



class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('autocomplete.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'autocomplete', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'autocomplete', **kwargs)


class Autocomplete(GenericClass):
    """TODO"""

    local_base_url = "autocomplete"

    @Time('autocomplete-list')
    def list(self, pattern, type="SHARING"):
        # pylint: disable=arguments-differ
        url = "%(base)s/%(pattern)s" % {
            'base': self.local_base_url,
            'pattern': pattern
        }
        param = {}
        param['type'] = type
        # FIXME
        encode = urllib.parse.urlencode(param, doseq=True)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)

    @CCache(CM, 'autocomplete-types', cache_duration=3600)
    def types(self):
        """TODO"""
        return self.core.options("enums/search_type")


    def get_rbu(self):
        rbu = ResourceBuilder("autocomplete")
        rbu.add_field('display')
        rbu.add_field('identifier')
        rbu.add_field('type')
        rbu.add_field('domain')
        rbu.add_field('firstName')
        rbu.add_field('lastName')
        rbu.add_field('mail')
        return rbu
