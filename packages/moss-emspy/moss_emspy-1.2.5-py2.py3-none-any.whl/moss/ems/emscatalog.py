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

import json
import logging

logger = logging.getLogger(__file__)


class EmsCatalogException(Exception):
    """
    Base catalog exception
    """


class EmsCatalog:
    """
    Base catalog class
    """

    def __init__(self, session, name, id=None, desc=None, entries=None, fields=None):
        self.name = name
        self.id = id
        self.description = desc
        self.data = self._read_catalog_values(entries)
        self.fields = fields

        self._session = session

    def _read_catalog_values(self, entries):
        """
        This fn is used to convert the catalog entries into a simple dictionary.
        :param entries: The ID of the feature.
        :type entries: int
        :returns:  dict -- a dictionary of catalog values, None on error.
        :raises: EmsCatalogException
        """
        data = {}
        try:
            for entry in entries:
                if "DCKEY" not in entry:
                    raise EmsCatalogException("Invalid catalog: DCKEY is missing")
                if "DCTXT" not in entry:
                    raise EmsCatalogException("Invalid catalog: DCTXT is missing")
            try:
                # data[entry["ID"]] = entry["DCTXT"]
                data = entries
            except KeyError:
                raise EmsCatalogException("Invalid catalog: DCKEY or DCTXT are missing")
        except TypeError:  # "'NoneType' object is not iterable" if entries is None
            return None

        return data

    def __getitem__(self, key):
        """
        Return the value of the catalog
        """
        logger.debug("Querying catalog %s using key %s", self.name, key)

        if key is None:
            logger.warning("Value is None. Ignoring catalog.")
            return key

        try:
            catalog_value = self.data[key]
        except KeyError:
            logger.warning("The key %s does not exist in catalog %s", key, self.name)
            catalog_value = key
        except IndexError:
            logger.error("Error reading catalog %s key %s", self, key)
            catalog_value = key

        # With some changes in code the returned value can be a dictionary.
        # Avoid this by doing another get. TODO Remove it and fix everything.

        if isinstance(catalog_value, dict):
            logger.debug("The value is a dictionary")
            return catalog_value.get("DCTXT", None)

        return catalog_value

    def add_entries(self, project_name, catalog_name, entries):
        """Add entries for a catalog of a project.

        Args:
            project_name: the project name
            catalog_name: the catalog name
            entries: a list of entries
        """

        url = "/".join(["rest", project_name, catalog_name.upper(), "addEntries"])

        request_parameters = {
            "f": "json",
            "entries": json.dumps(entries),
        }

        response_dict = self._ems_request(url, request_parameters, "POST")
        response_result = response_dict.get("addEntriesResult")

        if response_result is not None:
            response_success = response_result[0].get("success")

            if response_success:
                logger.info("Entry added correctly")
                return True
            else:
                logger.error("Error adding entry")
                return False

        else:
            raise EmsCatalogException("Invalid response from the server")

        return self

    def _ems_request(self, url, parameters, method="GET"):
        """
        Return a json response from a session
        """
        logger.debug("New request to %s parameters %s", url, parameters)

        if method == "POST":
            response = self._session.post(url, data=parameters)
        else:
            response = self._session.get(url, params=parameters)

        if response.status_code != 200:
            logger.error(
                "Error talking with ems. Url: %s Parameters: %s Status code: %s",
                url,
                parameters,
                response.status_code,
            )
            raise EmsCatalogException("Error talking with EMS")
        try:
            json_response = response.json()
        except ValueError as exception:
            logger.exception(
                "Response is not json. You are probably on the login website:%s",
                exception,
            )
        else:
            return json_response

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
