#! /usr/bin/env python
# -*- coding: utf-8 -*-


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
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#
"""TODO"""


from linshareapi.core import ResourceBuilder
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time as CTime
from linshareapi.admin.core import CM


class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, suffix, **kwargs):
        super().__init__('functionalities.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super().__init__(CM, 'functionalities', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super().__init__(CM, 'functionalities', **kwargs)


class Functionalities(GenericClass):
    """TODO"""

    @Time('list')
    @Cache(arguments=True)
    def list(self, domain_id=None, only_parents=False):
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        url = "functionalities?domainId={d}&subs={s!s}"
        url = url.format(d=domain_id, s=only_parents)
        json_obj = self.core.list(url)
        return [row for row in json_obj if row.get('displayable') is True]

    @Cache(discriminant="get", arguments=True)
    def get(self, func_id, domain_id=None):
        # pylint: disable=arguments-renamed
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        # pylint: disable=consider-using-f-string
        url = "functionalities/{identifier}?domainId={domain}".format(
            identifier=func_id,
            domain=domain_id
        )
        return self.core.get(url)

    @Invalid(whole_familly=True)
    def invalid(self):
        return "invalid : ok"

    @Time('update')
    @Invalid()
    def update(self, data):
        self.debug(data)
        return self.core.update("functionalities", data)

    @Time('reset')
    @Invalid()
    def reset(self, func_id, domain_id):
        """TODO"""
        self.log.debug("func_id: %s", func_id)
        self.log.debug("domain_id: %s", domain_id)
        if not func_id:
            raise ValueError("Missing func_id")
        if not domain_id:
            raise ValueError("Missing domain_id")
        data = {
            'identifier': func_id,
            'domain': domain_id
        }
        self.core.delete("functionalities", data)
        return self.get(func_id, domain_id=domain_id)

    def options_policies(self):
        """TODO"""
        return self.core.options("enums/policies")

    def get_rbu(self):
        rbu = ResourceBuilder("functionality")
        rbu.add_field('identifier', required=True)
        rbu.add_field('type')
        rbu.add_field('activationPolicy', required=False)
        rbu.add_field('configurationPolicy', extended=True, required=False)
        rbu.add_field('delegationPolicy', extended=True, required=False)
        rbu.add_field('parameters')
        rbu.add_field('parentIdentifier', extended=True)
        rbu.add_field('domain', extended=True, required=True)
        rbu.add_field('parentAllowParametersUpdate', extended=True)
        return rbu


class Functionalities5(GenericClass):
    """TODO"""

    local_base_url = "domains"
    local_resource = "functionalities"

    cache = {
        "familly": "functionalities-v5",
        "whole_familly": True,
    }

    @Time('list')
    @Cache(arguments=True)
    def list(self, domain_id=None, only_parents=False):
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        url = "domains/{domain}/functionalities?subs={s!s}"
        url = url.format(
                domain=domain_id,
                s=only_parents)
        return self.core.list(url)

    @Cache(discriminant="get", arguments=True)
    def get(self, func_id, domain_id="LinShareRootDomain"):
        # pylint: disable=arguments-renamed
        # pylint: disable=consider-using-f-string
        url = "domains/{domain}/functionalities/{identifier}".format(
            identifier=func_id,
            domain=domain_id
        )
        return self.core.get(url)

    @Invalid(whole_familly=True)
    def invalid(self):
        return "invalid : ok"

    @Time('update')
    @Invalid()
    def update(self, data):
        """ Update a list."""
        # pylint: disable=arguments-renamed
        # pylint: disable=consider-using-f-string
        self.debug(data)
        url = "%(base)s/%(d_uuid)s/%(resource)s/%(identifier)s" % {
            'base': self.local_base_url,
            'd_uuid': data.get('domain').get('uuid'),
            'resource': self.local_resource,
            'identifier': data.get('identifier')
        }
        return self.core.update(url, data)

    def reset(self, func_id, domain_id="LinShareRootDomain"):
        """TODO"""
        return self.delete(func_id, domain_id)

    @Time('reset')
    @Invalid()
    def delete(self, func_id, domain_id="LinShareRootDomain"):
        # pylint: disable=arguments-renamed
        # pylint: disable=consider-using-f-string
        url = "domains/{domain}/functionalities/{identifier}".format(
            identifier=func_id,
            domain=domain_id
        )
        return self.core.delete(url)

    def get_rbu(self):
        rbu = ResourceBuilder("functionality")
        rbu.add_field('identifier', required=True)
        rbu.add_field('type')
        rbu.add_field('activationPolicy', required=False)
        rbu.add_field('configurationPolicy', extended=True, required=False)
        rbu.add_field('delegationPolicy', extended=True, required=False)
        rbu.add_field('parameter')
        rbu.add_field('readonly')
        rbu.add_field('hidden')
        rbu.add_field('domain', extended=True, required=True)
        return rbu
