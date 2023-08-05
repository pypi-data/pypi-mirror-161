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


import copy
import json
import logging

from .emslayer import EmsLayer
from .emsqueryresult import EmsQueryResult

logger = logging.getLogger("ems_objectclass")


class ObjectClassException(Exception):
    """
    Handles exceptions for the objectClass
    """


class ObjectClass:
    """
    The Objectclass class
    """

    def __init__(self, project, session, object_definition):
        self._project = project
        self._session = session
        self.name = ""
        self.variantMaster = -1
        # the whole construction with this redundant variant_master is because
        # of the name convention and the assignment:
        # "if self.variant_master" needs an assigned self.variant_master AND
        # variantMaster does not fullfill the name convention
        # self.variant_master = 0

        for key, value in object_definition.items():
            setattr(self, key, value)
        #            if key == "variantMaster":
        #                self.variant_master = value
        if self.variantMaster == -1:
            self._total_features = self._count_features()
        else:
            self._total_features = 0

    def _count_features(self):
        """
        Counts the features of an objectclass
        """
        try:
            first_layer = self.layers[0]
        except KeyError:
            raise ObjectClassException("There are no layers in this objectclass")

        logger.debug("First layer is %s", first_layer)
        if first_layer is not None:

            url = "/".join(
                ["rest", self._project, self.name, first_layer.name, "query"]
            )
            parameters = {"f": "json", "where": "1=1", "returnCountOnly": "true"}

            logger.debug("Count features from %s", url)

            response = self._session.get(url, params=parameters)
            try:
                response_dict = response.json()
            except KeyError:
                return None

            count = 0
            try:
                count = response_dict["count"]
            except KeyError:
                logger.exception(
                    "There is no count key in the response: %s", response_dict
                )
                error_dictionary = response_dict["error"]
                logger.exception("Message: %s", error_dictionary["message"])
                logger.exception("Description: %s", error_dictionary["description"])
                logger.exception("Code: %s", error_dictionary["code"])
                raise ObjectClassException()
            return count

        return 0

    @property
    def id_field(self):
        #  type: ()->str
        """
        Return the name of the ID field for this objectclass
        """
        query_results = self.query(where="1=1")

        if query_results:
            try:
                id_field = query_results[0]
            except IndexError:
                id_field = "ID"
            return id_field
        else:
            # TODO Probably we should raise an error
            logger.warning(
                "Something is not correct requesting ID field %s.", query_results
            )
            return "ID"

    @property
    def has_variant(self):
        """
        Check if it has variant
        """
        return self.variantMaster != -1  # pylint:disable=no-member

    @property
    def layers(self):
        """
        The Layers for this ObjectClass

        Example
        --------

        >>> layers = objectclass.layers

        Returns:
            layers: A list of layers for the objectclass
        """

        url = "/".join(["rest", self._project, self.name, "layers"])
        parameters = {"f": "json"}

        response = self._session.get(url, params=parameters)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        layers = [
            EmsLayer(
                layer["name"],
                self.name,
                self._project,
                self._session,
                copy.deepcopy(layer),
            )
            for layer in response_dict["layers"]
        ]

        return layers

    def layer(self, layer_name):
        """
        Return a layer instance

        Example:
            >>> objectclass.layer("TEST_OBJECTCLASS")

        Args:
            layer_name: The name of the layer

        Returns:
            :layer: the layer instance with the given name
        """

        url = "/".join(["rest", self._project, self.name, layer_name])
        response = self._session.get(url)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        if "error" in response_dict.keys():
            logger.error("The layer %s does not exist", layer_name)
            raise ObjectClassException("Layer does not exist")
        else:
            layer = EmsLayer(
                layer_name,
                self.name,
                self._project,
                self._session,
                definition=response_dict,
            )
            return layer

    @property
    def features(self):
        """
        The features of this ObjectClass

        Example:
            >>> objectclass.features()

        Args:
            -

        Returns:
            :features: the features of the objectclass
        """
        first_layer = self.layers[0]

        if first_layer is not None:
            logger.debug("Getting features for %s", first_layer.name)
            pagination_query = first_layer.query(where="1=1")
            total_results = len(pagination_query)
            if total_results:
                result = list(pagination_query.resolve())[0]
                return result["features"]
            else:
                logger.debug("No layer found for %s", first_layer)
        return []

    def query(self, where="1=1", complete=False):
        """
        Query the objectClass

        Args:
            where: The SQL Expression to query the objectClass

        Returns:
            :list:
                - first element: the field name of the object id (default ID)
                - second element: a list of feature attributes
        """

        first_layer = self.layers[0]

        if first_layer:

            url = "/".join(
                ["rest", self._project, self.name, first_layer.name, "query"]
            )
            parameters = {"f": "json", "where": where}

            logger.debug("Getting features from %s", url)

            response = self._session.get(url, params=parameters)
            try:
                response_dict = response.json()
            except KeyError:
                return []
            try:
                features = response_dict["features"]
            except KeyError:
                logger.exception(
                    "Error running query %s. Server responded with %s",
                    url,
                    response_dict,
                )
                return []

            if complete is True:
                return response_dict
            else:
                return (
                    # the field name of the object id
                    # obviously in 99% it is "ID" but could be something else
                    response_dict["objectIdFieldName"],
                    [
                        EmsQueryResult(
                            self._session,
                            self._project,
                            self.name,
                            feature["attributes"],
                        )
                        for feature in features
                    ],
                )
        return []

    def clone_objectclass(self, objectclass_name):
        """
        Clone the objectClass

        Args:
            new objectclass name

        Returns:
            :bool: True if successfull, False otherwise
        """

        url = "/".join(["rest", self._project, self.name, "cloneObjectClass"])
        data = {
            "f": "json",
            "newObjectClassName": objectclass_name,
        }

        logger.debug(
            "Cloning the given objectclass %s to the new objectclass %s",
            self.name,
            objectclass_name,
        )

        response = self._session.post(url, params=data)
        try:
            response_dict = response.json()
        except KeyError:
            return False

        try:
            if response_dict["cloneObjectClassResult"]["success"] is False:
                error_dictionary = response_dict["cloneObjectClassResult"]["error"]

                logger.error("Message: %s", error_dictionary["message"])
                logger.error("Description: %s", error_dictionary["description"])
                logger.error("Code: %s", error_dictionary["code"])
                return False
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return False

    @property
    def tables(self):
        """
        Get the tables of an objectclass

        Args:
            -

        Returns:
            if successfull
                dictionary of tables
            else
                None
        """

        url = "/".join(["rest", self._project, self.name, "tables"])
        data = {
            "f": "json",
        }

        logger.debug("Query the tables of the objectclass %s", self.name)

        response = self._session.get(url, data=data)
        try:
            response_dict = response.json()
        except KeyError:
            logger.error("Error in tables query")
            raise ObjectClassException("Error in tables query")
        try:
            table_type = response_dict[0]["type"]
            logger.debug("First table type: '%s'", table_type)
            return response_dict
        except KeyError:
            logger.error("Error in tables query")
            raise ObjectClassException("Error in tables query")

    def update_objectclass(self, objectclass_name):
        """
        Updates the objectClass

        Args:
            objectclass_name: objectclass name to update

        Returns:
            :bool: True if successfull: False otherwise
        """

        url = "/".join(["rest", self._project, self.name, "updateObjectClass"])
        data = {"f": "json"}

        logger.debug("Updating the objectclass %s.", self.name)

        response = self._session.post(url, params=data)
        try:
            response_dict = response.json()
        except KeyError:
            return False

        try:
            if response_dict["updateObjectClassResult"]["success"] is False:
                error_dictionary = response_dict["updateObjectClassResult"]["error"]

                logger.error("Message: %s", error_dictionary["message"])
                logger.error("Description: %s", error_dictionary["description"])
                logger.error("Code: %s", error_dictionary["code"])
                return False
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return False

        return True

    def variants(self, feature_id):
        """
        Return the variants of the provided ID

        :param feature_id: The ID of the feature.
        :type feature_id: int
        :returns:  list -- the list of variants, None on error.
        :raises:
        """
        # TODO A lot of things to fix
        url = "/".join(["rest", self._project, self.name, str(feature_id), "variants"])
        parameters = {"f": "json"}

        logger.debug("Getting variants from %s", url)

        response = self._session.get(url, params=parameters)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        logger.debug(response_dict)
        try:
            variants = response_dict["variants"]
            return variants
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return None
        else:
            return None

    def create_variant(self, feature_id, variant_id, variants):
        """Create a new catalog for the current project.

        Args:
            str: name: the name of the catalog,
                 remember: the name may not contain blanks,
                 the name will be upper case in the database
            description: the description of the catalog
            fields: catalog entries

        Returns:
            bool: True = successfull, False otherwise
        """

        url = "/".join(
            [
                "rest",
                self._project,
                self.name,
                str(feature_id),
                "variant",
                str(variant_id),
                "create",
            ]
        )
        request_parameters = {"f": "json", "variants": json.dumps(variants)}

        response_dict = self._session.post(url, params=request_parameters)

        try:
            if response_dict["addCatalogResult"]["success"] is False:
                error_dictionary = response_dict["addCatalogResult"]["error"]

                logger.error("Message: %s", error_dictionary["message"])
                logger.error("Description: %s", error_dictionary["description"])
                logger.error("Code: %s", error_dictionary["code"])
                return False
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return False

        logger.info(
            "Added successfully the catalog '%s'.",
        )
        return True

    def __len__(self):
        """
        Returns the total number of features
        """
        return self._total_features

    def __repr__(self):
        """
        The name of the ObjectClass
        """
        return self.name
