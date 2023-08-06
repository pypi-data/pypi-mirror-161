#! /usr/bin/env python3
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
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#




from linshareapi.core import ResourceBuilder
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time as CTime
from linshareapi.admin.core import CM

# ylint: disable=C0111
# Missing docstring
# ylint: disable=R0903
# Too few public methods
class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, suffix, **kwargs):
        super().__init__('mail_activations.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super().__init__(CM, 'mail_activations', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    def __init__(self, **kwargs):
        super().__init__(CM, 'mail_activations', **kwargs)


class MailActivations(GenericClass):
    """TODO"""

    @Time('list')
    @Cache(arguments=True)
    def list(self, domain_id=None):
        """TODO"""
        # pylint: disable=arguments-differ
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        url = "mail_activations?domainId={d}"
        url = url.format(d=domain_id)
        json_obj = self.core.list(url)
        return json_obj

    @Cache(discriminant="get", arguments=True)
    def get(self, mail_activation_id, domain_id=None):
        """TODO"""
        # pylint: disable=arguments-differ
        # pylint: disable=too-few-public-methods
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        json_obj = self.core.get("mail_activations/"+ mail_activation_id +"?domainId=" +
                                 domain_id)
        return json_obj

    @Invalid(whole_familly=True)
    def invalid(self):
        return "invalid : ok"

    @Time('update')
    @Invalid()
    def update(self, data):
        self.debug(data)
        return self.core.update("mail_activations", data)

    @Time('reset')
    @Invalid()
    def reset(self, mail_activation_id, domain_id):
        """TODO"""
        self.log.debug("mail_activation_id: %s", mail_activation_id)
        self.log.debug("domain_id: %s", domain_id)
        if not mail_activation_id:
            raise ValueError("Missing mail_activation_id")
        if not domain_id:
            raise ValueError("Missing domain_id")
        data = {
            'identifier': mail_activation_id,
            'domain': domain_id
        }
        self.core.delete("mail_activations", data)
        return self.get(mail_activation_id, domain_id=domain_id)


    def options_policies(self):
        """TODO"""
        return self.core.options("enums/policies")

    def get_rbu(self):
        rbu = ResourceBuilder("functionality")
        rbu.add_field('identifier', required=True)
        rbu.add_field('activationPolicy', extended=True, required=False)
        rbu.add_field('configurationPolicy', required=False)
        rbu.add_field('delegationPolicy', extended=True, required=False)
        rbu.add_field('enable')
        rbu.add_field('domain', extended=True, required=True)
        return rbu
