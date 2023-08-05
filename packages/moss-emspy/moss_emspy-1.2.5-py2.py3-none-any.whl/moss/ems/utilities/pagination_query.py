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

from ..emscatalog import EmsCatalog

logger = logging.getLogger(__file__)


class EmsPaginationQueryException(Exception):
    """
    Exception for EmsLayer
    """


class PaginationQuery:
    """
    This will run a query using pagination.
    """

    def __init__(self, session, url, project, **kwargs):
        self.session = session
        self.url = url
        self.project = project
        self.query_parameters = kwargs

        # for key, value in kwargs.items():
        #    setattr(self, key, value)

        self.length = self._result_length()
        if self.length < 0:
            raise EmsPaginationQueryException("An error occured in querying the layer.")

        self._saved_catalogs = {}

    def _result_length(self):
        """
        A query to get the total number of results
        """
        params = {
            "f": "json",
            "returnCountOnly": True,
            "where": self.query_parameters["where"],
        }

        if "variants" in self.query_parameters:
            params["variants"] = self.query_parameters["variants"]

        if "geometry" in self.query_parameters:
            params["geometry"] = json.dumps(self.query_parameters["geometry"])
            params["geometryType"] = "esriGeometryEnvelope"

        response = self.session.get(self.url, params=params)
        response_dict = response.json()

        if "count" not in response_dict:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])

        return response_dict.get("count", -1)

    def __len__(self):
        if isinstance(self.length, str):
            return 0
        else:
            return self.length

    def _catalog(self, catalog_name):
        """
        Return the catalog.
        """

        url = "/".join(["rest", self.project, catalog_name, "query"])
        request_parameters = {"f": "json", "query": "1=1"}
        response = self.session.get(url, params=request_parameters)
        response_dict = response.json()
        # logger.debug("Response catalog %s", response_dict)
        catalog = EmsCatalog(
            name=catalog_name, session=response_dict, entries=response_dict["entries"]
        )

        return catalog

    def _process_catalog(self, query_results):
        """
        Replace the catalogs values in the result
        """

        # Using the fields we create a dictionary with as key the field name
        # and as value the catalog where this entry exist
        field_catalog = {
            field["name"]: field["catalogName"]
            for field in query_results["fields"]
            if "catalogName" in field
        }

        for key, feature in enumerate(query_results["features"]):
            for attribute, value in list(feature["attributes"].items()):

                logger.debug(
                    "Current attribute is %s current value is %s", attribute, value
                )
                if attribute in field_catalog:

                    catalog_name = field_catalog[attribute]
                    logger.debug("Catalog name %s", catalog_name)

                    if catalog_name in self._saved_catalogs.keys():
                        logger.debug("Catalog already stored")
                        catalog = self._saved_catalogs[catalog_name]
                    else:
                        catalog = self._catalog(catalog_name)
                        self._saved_catalogs[catalog_name] = catalog

                        logger.debug("Stored catalog %s", self._saved_catalogs)

                    # Update the values with the values in catalog
                    query_results["features"][key]["attributes"][attribute] = catalog[
                        value
                    ]
        return query_results

    def resolve(self, page_size=500, with_catalog=False):
        """
        Run the query to get the result

        :param page_size: The number of records to fetch.
        :type page_size: int
        :param with_catalog: A switch to replace the catalog values of the result
        :type with_catalog: bool
        :returns:  the data of the pagination query according to the parameters set
        :raises:
        """
        record_offset = 0
        if "geometry" in self.query_parameters:
            self.query_parameters["geometry"] = json.dumps(
                self.query_parameters["geometry"]
            )
            self.query_parameters["geometryType"] = "esriGeometryEnvelope"

        while True:
            pagination_params = {
                "resultRecordCount": page_size,
                "resultOffset": record_offset,
            }

            params = self.query_parameters.copy()
            params.update(pagination_params)

            response = self.session.post(self.url, data=params)

            response.raise_for_status()

            data = response.json()

            if record_offset > self.length:
                break

            if with_catalog:

                yield self._process_catalog(data)
            else:
                yield data

            record_offset += page_size
