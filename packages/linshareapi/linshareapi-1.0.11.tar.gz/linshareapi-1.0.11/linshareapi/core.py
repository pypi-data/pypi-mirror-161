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
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#




import os
import re
import json
import logging
import logging.handlers
import datetime
from collections import OrderedDict
from http.client import HTTPConnection
from requests import Session
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
from requests_toolbelt.utils import dump
from requests_toolbelt import (MultipartEncoder, MultipartEncoderMonitor)
from progressbar import ProgressBar, FileTransferSpeed, Bar, ETA, Percentage, DataSize



# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

LOG = logging.getLogger('linshareapi.core')

class LinShareException(Exception):
    pass

#    def __init__(self, code, msg, *args, **kwargs):
#        super(LinShareException, self).__init__(*args, **kwargs)
#        self.code = code
#        self.msg = msg


def extract_file_name(content_dispo):
    """Extract file name from the input request body"""
    content_dispo = content_dispo.strip('"')
    file_name = ""
    for key_val in content_dispo.split(';'):
        param = key_val.strip().split('=')
        if param[0] == "filename":
            file_name = param[1].strip('"')
            break
    return file_name


def get_default_widgets():
    widgets = [
        FileTransferSpeed(),
        ' <<<',
        Bar(),
        '>>> ',
        Percentage(),
        ' - ',
        DataSize(),
        ' - ',
        ETA()
    ]


def create_callback(encoder):
    """TODO"""
    encoder_len = encoder.len
    progress = ProgressBar(widgets=get_default_widgets(), maxval=encoder_len)
    def callback(monitor):
        progress.update(monitor.bytes_read)
    return callback, progress


def trace_session(session):
    for header in session.headers.items():
        LOG.debug("session.header: %s", header)
    for cookie in session.cookies.items():
        LOG.debug("session.cookie: %s", cookie)


def trace_request(request):
    for header in request.headers.items():
        LOG.debug("request.header: %s", header)
    for cookie in request.cookies.items():
        LOG.debug("request.cookie: %s", cookie)

class ApiNotImplementedYet(object):

    def __init__(self, corecli, version, end_point):
        self.core = corecli
        self.end_point = end_point
        self.version = version

    def __getattr__(self, name):
        raise NotImplementedError(
            "The current end point '%(api)s' is not supported in the api version '%(version)s'." % {
                'api': self.end_point,
                'version': self.version})


class HTTPJwtAuth(AuthBase):
    """TODO"""

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return self.token == getattr(other, 'token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer " + self.token
        return r

class CoreCli(object):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, host, user, password, verbose=False, debug=0,
                 realm="Name Of Your LinShare Realm", verify=True,
                 auth_type="plain"):
        classname = str(self.__class__.__name__.lower())
        self.log = logging.getLogger('linshareapi.' + classname)
        self.verbose = verbose
        self.debug = debug
        if debug >= 3:
            HTTPConnection.debuglevel = 2
        self.host = host
        self.user = user
        self.last_req_time = None
        self.cache_time = 60
        self.nocache = False
        self.base_url = ""
        if not host:
            raise ValueError("invalid host : host url is not set !")
        if not user:
            raise ValueError("invalid user : " + str(user))
        if not password:
            raise ValueError("invalid password : password is not set ! ")
        if not realm:
            realm = "Name Of Your LinShare Realm"
        self.session = Session()
        self.session.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=UTF-8',
            }
        )
        if auth_type == "plain":
            self.session.auth = HTTPBasicAuth(user, password)
        elif auth_type == "jwt":
            self.session.auth = HTTPJwtAuth(password)
        else:
            raise ValueError("Invalid auth_type value: " + auth_type)
        self.session.verify = verify

    def get_full_url(self, url_frament):
        root_url = self.host
        if root_url[-1] != "/":
            root_url += "/"
        root_url += self.base_url
        if root_url[-1] != "/":
            root_url += "/"
        root_url += url_frament
        return root_url

    def auth(self, quiet=False):
        url = self.get_full_url("authentication/authorized")
        self.log.debug("list url : %s", url)
        request = self.session.get(url)
        self.log.debug("request: %s", request)
        if request:
            self.log.debug("auth url : ok")
            return True
        if request.status_code == 401:
            self.log.debug("Authentication failed: %s: %s", request.status_code, request.text)
            trace_request(request)
            error_code = request.headers.get('X-Linshare-Auth-Error-Code')
            error_msg = request.headers.get('X-Linshare-Auth-Error-Msg')
            self.log.debug("X-Linshare-Auth-Error-Code: %s: Msg: %s", error_code, error_msg)
            if error_code == '1004':
                raise LinShareException(error_code, error_msg)
            if not quiet:
                self.log.error("Authentication failed: error code=%s: %s", error_code, error_msg)
        return False

    def process_request(self, request, url, force_nocontent=False):
        """TODO"""
        self.log.debug("url : %s", url)
        self.log.debug("request: %s", request)
        trace_session(self.session)
        trace_request(request)
        self.log.debug("request.text: %s", request.text)
        self.log.debug(
            "list url : %(url)s : request time : %(time)s",
            {
                "url": url,
                "time": self.last_req_time
            }
        )
        if request:
            if request.status_code == 204:
                return True
            if force_nocontent:
                return request.text
            return request.json()
        else:
            code = request.status_code
            msg = request.text
            self.log.debug("headers: %s", request.headers)
            content_type = request.headers.get('Content-Type')
            self.log.debug("Content-Type: %s", content_type)
            content_length = request.headers.get('Content-Length')
            self.log.debug("Content-Length: %s", content_length)
            content_dispo = request.headers.get('Content-Disposition')
            self.log.debug("Content-Disposition: %s", content_dispo)
            if not force_nocontent and request.status_code in [400, 403, 404]:
                if content_type == 'application/json':
                    json_obj = request.json()
                    code = json_obj.get('errCode')
                    msg = json_obj.get('message')
                self.log.debug("Server error code: %s", code)
                self.log.debug("Server error message: %s", msg)
            raise LinShareException(code, msg)

    def list(self, url):
        """ List ressources store into LinShare."""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        request = self.session.get(url)
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        return self.process_request(request, url)

    def list_browse_all_pages(self, url):
        """ List ressources store into LinShare."""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        request = self.session.get(url)
        res = self.process_request(request, url)
        if 'Current-Page-Size' in request.headers:
            last = request.headers.get('Last') == 'true'
            self.log.error("Last: %s", last)
            cpt = 0
            while not last:
                current_page = request.headers.get('Current-Page')
                self.log.error("Current-Page: %s", current_page)
                next_page = url + "&page=" + str(cpt)
                if '?' not in url:
                    next_page = url + "?page=" + str(cpt)
                request = self.session.get(next_page)
                last = request.headers.get('Last') == 'true'
                cpt += 1
                res += self.process_request(request, url)
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        return res


    def get(self, url):
        """Get a ressource store into LinShare."""
        return self.list(url)

    def delete(self, url, data=None):
        """Delete a ressource store into LinShare."""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        query = {"url": url}
        if data:
            self.log.debug("using payload for deleting the current object : %s", data)
            # post_data = json.dumps(data)
            # post_data = post_data.encode('utf-8')
            query["data"] = json.dumps(data)
        request = self.session.delete(**query)
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        return self.process_request(request, url)

    def options(self, url):
        """TODO"""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        request = self.session.options(url)
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        return self.process_request(request, url)

    def head(self, url):
        """TODO"""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        request = self.session.head(url)
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        try:
            return self.process_request(request, url, force_nocontent=True)
        except LinShareException:
            return False

    def create(self, url, data):
        """Create a ressource store into LinShare."""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        request = self.session.post(url, data=json.dumps(data))
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        return self.process_request(request, url)

    def update(self, url, data):
        """Create a ressource store into LinShare."""
        url = self.get_full_url(url)
        starttime = datetime.datetime.now()
        request = self.session.put(url, data=json.dumps(data))
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        return self.process_request(request, url)

    def upload(self, file_path, url, description=None, file_name=None,
               progress_bar=True, **kwargs):
        self.log.debug("kwargs is : %s", kwargs)
        url = self.get_full_url(url)
        file_size = os.path.getsize(file_path)
        self.log.debug("file_size is : %s", file_size)
        if not file_name:
            file_name = os.path.basename(file_path)
        self.log.debug("file_name is : %s", file_name)
        if file_size <= 0:
            msg = (
                "The file '{filename}' can not be uploaded"
                "because its size is less or equal to zero."
            )
            msg.format({"filename": file_name})
            raise LinShareException("-1", msg)
        with open(file_path, 'rb') as file_stream:
            fields = {
                'filesize': str(file_size),
                'file': (file_name, file_stream)
            }
            if description:
                fields["description"] = description

            if progress_bar:
                multi = MultipartEncoder(fields=fields)
                callback, progress_bar = create_callback(multi)
                encoder = MultipartEncoderMonitor(multi, callback)
            else:
                encoder = MultipartEncoder(fields=fields)
            starttime = datetime.datetime.now()
            request = self.session.post(
                url,
                headers={'Content-Type': encoder.content_type},
                data=encoder)
            if progress_bar:
                progress_bar.finish()
            trace_session(self.session)
            trace_request(request)
            endtime = datetime.datetime.now()
            self.last_req_time = str(endtime - starttime)
            return self.process_request(request, url)

    def download(self, uuid, url, forced_file_name=None,
                 progress_bar=True, chunk_size=256,
                 directory=None, overwrite=False):
        """ download a file from LinShare using its rest api.
        This method could throw exceptions like urllib2.HTTPError."""
        self.last_req_time = None
        url = self.get_full_url(url)
        self.log.debug("download url : %s", url)
        starttime = datetime.datetime.now()
        request = self.session.get(url, stream=True)
        file_name = uuid
        self.log.debug("url : %s", url)
        self.log.debug("request: %s", request)
        trace_session(self.session)
        trace_request(request)
        if not request:
            code = "-1"
            msg = request.text
            self.log.debug("headers: %s", request.headers)
            if request.status_code in [400, 403, 404]:
                json_obj = request.json()
                code = json_obj.get('errCode')
                msg = json_obj.get('message')
            self.log.debug("Server error code: %s", code)
            self.log.debug("Server error message: %s", msg)
            raise LinShareException(code, msg)
        content_type = request.headers.get('Content-Type')
        self.log.debug("Content-Type: %s", content_type)
        content_length = request.headers.get('Content-Length')
        self.log.debug("Content-Length: %s", content_length)
        content_dispo = request.headers.get('Content-Disposition')
        self.log.debug("Content-Disposition: %s", content_dispo)
        self.log.debug("Content-Transfer-Encoding: %s",
                       request.headers.get("Content-Transfer-Encoding"))
        if not content_length:
            self.log.error("Content-Length header missing. download aborted.")
        file_size = int(content_length.strip())
        if forced_file_name:
            file_name = forced_file_name
        else:
            if content_dispo:
                content_dispo = content_dispo.strip()
                file_name = extract_file_name(content_dispo)
        if directory:
            if os.path.isdir(directory):
                file_name = directory + "/" + file_name
        self.log.debug("file_name: %s", file_name)
        if os.path.isfile(file_name):
            if not overwrite:
                cpt = 1
                while 1:
                    if not os.path.isfile(file_name + "." + str(cpt)):
                        file_name += "." + str(cpt)
                        break
                    cpt += 1
            else:
                self.log.warn("'%s' already exists. It was overwriten.",
                              file_name)
        with ProgressBar(widgets=get_default_widgets(), maxval=file_size) as progress:
            with open(file_name, 'wb') as file_stream:
                bytes_read = 0
                for line in request.iter_content(chunk_size=chunk_size):
                    if line:
                        bytes_read += len(line)
                        if progress_bar:
                            if bytes_read > file_size:
                                # it may happen when content is text data and
                                # reverse proxies compressed it.
                                self.log.debug(
                                    "bytes_read greater than content length: %s/%s",
                                    bytes_read, file_size)
                            else:
                                progress.update(bytes_read)
                        file_stream.write(line)
        endtime = datetime.datetime.now()
        self.last_req_time = str(endtime - starttime)
        self.log.debug(
            "download url : %(url)s : request time : %(time)s",
            {
                "url": url,
                "time": self.last_req_time
            }
        )
        return (file_name, self.last_req_time)


class ResourceBuilder(object):
    """ Helper to create a ressource """

    """Create a new ResourceBuilder:

        Keyword arguments:
        name        -- resource name (display purpose)
        required    -- defined default required value for all fields.
    """
    def __init__(self, name=None, required=False):
        self._name = name
        self._fields = OrderedDict()
        self._required = required
        l_name = "rbu"
        if name:
            l_name = "rbu:" + name
        self.log = logging.getLogger(l_name)

    def add_hook(self, key, hook):
        field = self._fields.get(key, None)
        if field is not None:
            field['hook'] = hook

    def add_field(self, field, arg=None, value=None, extended=False,
                  hidden=False, e_type=str, required=None, not_empty=False,
                  skip=False):
        """Add a new field to the current ResourceBuilder.

           Keyword arguments:
           field    -- field name
           arg      -- name of the attribute name in arg object (argparse)
           value    -- a default for this field, used for resource creation.
           extended -- If set to true, the current field will be display in
                       extended list mode only.
           hidden   -- If set to true, the current field won't be exposed
                       as available keys.
           e_type   -- field data type (default str): int, float, str
           required -- True if the current field is required for create
                       and update methods
           not_empty -- True if the current field is required and it is not
                       an empty string
           skip      -- Do not send it to the server
        """
        if required is None:
            required = self._required
        if arg is None:
            arg = re.sub('(?!^)([A-Z]+)', r'_\1', field).lower()
        self._fields[field] = {
            'field': field,
            'value': value,
            'arg': arg,
            'extended': extended,
            'required': required,
            'not_empty': not_empty,
            'e_type': e_type,
            'hidden': hidden,
            'skip': skip
        }

    def get_keys(self, extended=False):
        res = []
        for field in list(self._fields.values()):
            if field['hidden']:
                continue
            if not field['extended']:
                res.append(field['field'])
            if extended and field['extended']:
                res.append(field['field'])
        return res

    def get_fields(self, extended=False, full=False):
        res = []
        if extended:
            for field in list(self._fields.values()):
                if field['extended']:
                    res.append(field['field'])
        elif full:
            for field in list(self._fields.keys()):
                res.append(field)
        else:
            for field in list(self._fields.values()):
                if not field['extended']:
                    res.append(field['field'])
        return res

    def set_arg(self, key, arg):
        field = self._fields.get(key, None)
        if field is not None:
            field['arg'] = arg

    def get_value(self, key):
        field = self._fields.get(key, None)
        if field is not None:
            return field['value']
        else:
            return None

    def set_value(self, key, value):
        field = self._fields.get(key, None)
        if field is not None:
            field['value'] = value

    def to_resource(self):
        ret = {}
        for field in list(self._fields.values()):
            if not field['skip']:
                ret[field['field']] = field['value']
        return ret

    def load_from_args(self, namespace):
        for field in list(self._fields.values()):
            self.log.debug("config: %s", field)
            value = getattr(namespace, field['arg'], None)
            if value is not None:
                if 'hook' in field:
                    value = field['hook'](value, self)
                field['value'] = value

    def copy(self, data):
        if isinstance(data, dict):
            self.log.debug("dict")
            for field, val in list(self._fields.items()):
                self.log.debug("field: %s", field)
                self.log.debug("config: %s", val)
                value = data.get(field, None)
                self.log.debug("value: %s", value)
                if value is not None:
                    val['value'] = value
        elif isinstance(data, ResourceBuilder):
            self.log.debug("rbu")
            for field, val in list(self._fields.items()):
                self.log.debug("field: %s", field)
                self.log.debug("config: %s", val)
                value = data[field]['value']
                self.log.debug("value: %s", value)
                val['value'] = value
        else:
            self.log.debug("type: %s", type(data))
            raise ValueError("Invalid input data")

    def __str__(self):
        res = []
        res.append("[" + self._name + "] {")
        for field in self._fields.values():
            res.append("  " + str(field))
        return "\n".join(res) + "\n}"

    def check_required_fields(self):
        for field in list(self._fields.values()):
            if field['required']:
                value = field['value']
                if field['not_empty']:
                    self.log.debug("not_empty flag enabled for '%s'.",
                                   field['field'])
                    if not value:
                        raise ValueError(
                            "missing value for required field (empty) : " + field['field'])
                if value is None:
                    raise ValueError("missing value for required field : "
                                     + field['field'])
                e_type = field['e_type']
                if e_type == int:
                    int(value)
                if e_type == float:
                    float(value)


class GenericClass(object):
    def __init__(self, corecli):
        self.core = corecli
        self.log = logging.getLogger('linshareapi.core.api')
        self.last_req_time = None

    def get_rbu(self):
        # pylint: disable=R0201
        rbu = ResourceBuilder("generic")
        return rbu

    def get_resource(self):
        return self.get_rbu().to_resource()

    def debug(self, data):
        self.log.debug("input data :")
        self.log.debug(json.dumps(data, sort_keys=True, indent=2))

    def _check(self, data):
        rbu = self.get_rbu()
        rbu.copy(data)
        rbu.check_required_fields()
