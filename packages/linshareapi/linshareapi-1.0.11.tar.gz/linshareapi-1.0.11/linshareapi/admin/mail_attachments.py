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
# Copyright 2019 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#




import urllib
import os
import datetime

from linshareapi.core import ResourceBuilder
from linshareapi.core import LinShareException
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time
from linshareapi.admin.core import Cache
from linshareapi.admin.core import Invalid
from requests_toolbelt import MultipartEncoder



class MailAttachments(GenericClass):
    """MailAttachments"""

    # Mandatory: define the base api for the REST resource
    local_base_url = "mail_attachments"
    cache = {"familly": "mail_attachments"}

    def get_rbu(self):
        rbu = ResourceBuilder("mail_attachments")
        rbu.add_field('uuid')
        rbu.add_field('name')
        rbu.add_field('cid')
        rbu.add_field('enable', value="True")
        rbu.add_field('enableForAll', value="True")
        rbu.add_field('language')
        rbu.add_field('description')
        rbu.add_field('mailConfig', extended=True)
        return rbu

    @Time('list')
    # @Cache(discriminant=False, arguments=True)
    def list(self, config_uuid):
        # pylint: disable=arguments-differ
        url = "{base}".format(
            base=self.local_base_url
        )
        param = {}
        param['configUuid'] = config_uuid
        encode = urllib.parse.urlencode(param)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)

    @Time('create')
    # @Invalid(whole_familly=True)
    def create(self, file_path, data, file_name=None):
        self.last_req_time = None
        url = "{base}".format(
            base=self.local_base_url
        )
        url = self.core.get_full_url(url)
        self.log.debug("upload url : %s", url)
        # Generating datas and headers
        file_size = os.path.getsize(file_path)
        self.log.debug("file_path is : %s", file_path)
        if not file_name:
            file_name = os.path.basename(file_path)
        self.log.debug("file_name is : %s", file_name)
        if file_size <= 0:
            msg = "The file '%(filename)s' can not be uploaded because its size is less or equal to zero." % {"filename": str(file_name)}
            raise LinShareException("-1", msg)
        with open(file_path, 'rb') as file_stream:
            fields = {
                'filesize': str(file_size),
                'file': (file_name, file_stream),
            }
            for field, value in data.items():
                if value is not None:
                    if field == "mailConfig":
                        fields["mail_config"] = str(value)
                    else:
                        fields[field] = str(value)
            if fields.get('language'):
                fields["enableForAll"] = str(False)
            self.log.debug("fields: %s", fields)
            encoder = MultipartEncoder(fields=fields)
            self.core.session.headers.update({'Content-Type': encoder.content_type})
            starttime = datetime.datetime.now()
            request = self.core.session.post(url, data=encoder)
            endtime = datetime.datetime.now()
            self.last_req_time = str(endtime - starttime)
            return self.core.process_request(request, url)
