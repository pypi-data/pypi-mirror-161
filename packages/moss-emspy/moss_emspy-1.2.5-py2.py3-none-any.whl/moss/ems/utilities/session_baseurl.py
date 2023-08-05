#
# The MIT License (MIT)
# Copyright (c) 2021 M.O.S.S. Computer Grafik Systeme GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT,TORT OR OTHERWISE, ARISING FROM, OUT
# OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import logging

from requests import Session
from requests.compat import urljoin

logger = logging.getLogger(__file__)


class SessionBaseUrl(Session):
    """
    This subclass will allow to store the base address
    of the service. This will avoid to always pass the base url.
    """

    def __init__(self, base_url, token=None):
        self.base_url = base_url
        # self.token = token
        super(SessionBaseUrl, self).__init__()

    def request(self, method, url, *args, **kwargs):
        """Send a Rest request to the url with args and additional kwargs

        :param method: "GET" or "POST"
        :type method: str
        :param url: The url to send the request to
        :type url: str
        :param args: a variable number of arguments for the request
        :type args: args
        :param kwargs: a keyworded, variable-length argument list for the request
        :type kwargs: kwargs
        :returns: The html response dict for the request
        :raises:
        """
        url = urljoin(self.base_url, url)

        # if "params" in kwargs:
        #    kwargs["params"] = {**kwargs["params"], "token": self.token}

        return super(SessionBaseUrl, self).request(method, url, *args, **kwargs)
