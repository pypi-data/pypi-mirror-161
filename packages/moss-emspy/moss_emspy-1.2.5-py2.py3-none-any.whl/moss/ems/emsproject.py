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

from anytree import Node, PreOrderIter, RenderTree, find_by_attr
from anytree.exporter import DictExporter

from .emscatalog import EmsCatalog
from .emsobjectclass import ObjectClass

logger = logging.getLogger(__file__)


class EmsProjectException(Exception):
    """
    Base Exception for EmsProject
    """


class EmsProject:
    """
    Project
    """

    def __init__(self, session, project_definition):
        """
        The class will be initialized using the answer from EMS.
        With this solution we have access to all the EMS attributes
        """

        self._session = session
        self.name = ""  # because of pylint

        for key, value in project_definition.items():
            setattr(self, key, value)

    def __repr__(self):
        return str(self.name)

    @property
    def catalogs(self):
        """
        The list of all catalogs for the project
        """

        url = "/".join(["rest", self.name, "catalogs"])
        request_parameters = {"f": "json"}

        response_dict = self._ems_request(url, request_parameters)

        try:
            catalogs = response_dict["catalogs"]
        except KeyError:
            logger.debug("Getting catalogs %s", response_dict)
            raise EmsProjectException("There are no catalogs in the response")
        return [
            EmsCatalog(
                self._session,
                name=catalog["name"],
                id=catalog["id"],
                desc=catalog["description"],
                fields=catalog["fields"],
            )
            for catalog in catalogs
        ]

    def catalog(self, name):
        """
        Return the catalog.

        Args:
            string: name The name of the catalog
        """

        url = "/".join(["rest", self.name, name.upper(), "query"])
        request_parameters = {"f": "json", "query": "1=1"}

        response_dict = self._ems_request(url, request_parameters)
        catalog = EmsCatalog(
            self._session,
            name=name,
            entries=response_dict["entries"],
            fields=response_dict["fields"],
        )

        return catalog

    @property
    def objectclasses(self):
        """
        The list of the objectClasses for the current Project
        """

        url = "/".join(["rest", self.name, "objectClasses"])
        request_parameters = {"f": "json"}

        response_dict = self._ems_request(url, request_parameters)

        return [
            ObjectClass(
                session=self._session, project=self.name, object_definition=objectclass
            )
            for objectclass in response_dict["objectClasses"]
        ]

    def objectclass(self, name):
        """
        Returns the object with the specified name.

        Examples:
            Return the objectClass with the provided name

            >>> print(my_project.objectclass("test_project"))
            test_project

        Args:
            name: Name of the objectClass

        Returns:
            objectclass: An Objectclass instance
        """

        url = "/".join(["rest", self.name, "objectClasses"])
        request_parameters = {"f": "json"}

        response_dict = self._ems_request(url, request_parameters)
        objectclass = next(
            iter(filter(lambda x: x["name"] == name, response_dict["objectClasses"])),
            None,
        )

        if objectclass is not None:
            return ObjectClass(
                session=self._session, project=self.name, object_definition=objectclass
            )

        logging.info("There is no objectClass with name = %s", name)
        return None

    def add_objectclass(self, objectclass):
        """
        Create a new objectclass for a given project.

        Args:
            objectclass: entries necessary for the objectclass (layers, tables, ..)

        Returns:
            integer: the new object id, -99: if an error occurs

        Raises:
            EmsProjectException
        """
        if self.name is None:
            raise EmsProjectException("You have to set the name of a project")
        if objectclass is None:
            raise EmsProjectException("You have to provide a valid objectclass")

        url = "/".join(["rest", self.name, "addObjectClass"])

        parameters = {}
        for key, value in objectclass.items():
            if isinstance(value, (list, dict)):
                parameters[key] = json.dumps(value)
            else:
                parameters[key] = value

        response_dict = self._ems_request(url, parameters, "POST")

        try:
            if response_dict["addObjectClassResult"]["success"] is False:
                error_dictionary = response_dict["addObjectClassResult"]["error"]
                logger.error("Message: %s", error_dictionary["message"])
                logger.error("Description: %s", error_dictionary["description"])
                logger.error("Code: %s", error_dictionary["code"])
                return -99
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return -99

        logger.info("Added successfully the objectclass '%s'.", objectclass["name"])
        return response_dict["addObjectClassResult"]["objectId"]

    def delete_objectclass(self, objectclass_id):
        """
        Deletes an objectclass for a given project.

        Args:
            project_name: the name of the project
            objectclass: the name of the objectclass

        Returns:
            bool: True = successfull, False otherwise
        """

        if isinstance(objectclass_id, int) is not True:
            logger.error("The parameter '%s' is not an integer value", objectclass_id)

        url = "/".join(["rest", self.name, "deleteObjectClass"])

        request_parameters = {"f": "json", "objectClassId": objectclass_id}
        response_dict = self._ems_request(url, request_parameters, "POST")

        if response_dict["deleteObjectClassResult"]["success"] is False:
            logger.error(
                "Message: %s",
                response_dict["deleteObjectClassResult"]["error"]["message"],
            )
            logger.error(
                "Description: %s",
                response_dict["deleteObjectClassResult"]["error"]["description"],
            )
            logger.error(
                "Code: %s", response_dict["deleteObjectClassResult"]["error"]["code"]
            )
            return False

        logger.info("Deleted the objectclass with id %s.", objectclass_id)
        return True

    def add_catalog(self, name, description=None, fields=None):
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
        if fields is None:
            fields = []

        url = "/".join(["rest", self.name, "addCatalog"])
        request_parameters = {"f": "json", "name": name, "fields": json.dumps(fields)}

        if description is not None:
            request_parameters["description"] = description

        response_dict = self._ems_request(url, request_parameters, "POST")

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

        logger.info("Added successfully the catalog '%s'.", name)
        return True

    def delete_catalog(self, catalog_name):
        """
        Delete a catalog by name for the current project.

        Args:
            catalog_name: the name of the catalog

        Returns:
            bool: True = successfull, False otherwise
        """

        # firstly a mapping of the name to the name is needed
        url = "/".join(["rest", self.name, "catalogs"])
        request_parameters = {
            "f": "json",
        }
        catalog_response = self._ems_request(url, request_parameters, "GET")
        catalogs = catalog_response.get("catalogs")

        catalogs_search = list(
            filter(lambda catalog: catalog["name"] == catalog_name.upper(), catalogs)
        )

        if catalogs_search:
            catalog_id = catalogs[0]["id"]
        else:
            logger.error("There is no catalog called %s", catalog_name)
            return False

        # now we have a valid id
        url = "/".join(["rest", self.name, "deleteCatalog"])
        request_parameters = {
            "f": "json",
            "catalogId": catalog_id,
        }
        response_dict = self._ems_request(url, request_parameters, "POST")

        response_result = response_dict.get("deleteCatalogResult")
        # With a wrong id there is no key deleteCatalogResult
        if response_result is None:
            logger.debug("Response to deleteCatalog %s", response_result)
            logger.error("The provided id does not exist")
            return False

        request_success = response_result.get("success")

        if request_success:
            logger.info("Deleted successfully the catalog ")
            return True
        else:
            logger.error("Can not delete Catalog ")
            return False

    def variants_tree(self):
        """
        Return a dict and a Iterable with the traversing structure of the variants tree
        """

        complete_list = []
        search_expression = "ID>=1"

        objectclasses = self.objectclasses

        # Find the VNT Master Objectclass
        variant_master_objectclass = next(
            (
                item for item in objectclasses if item.objectClassType == "VNTMASTER"
            ),  # type: ignore
            None,
        )

        # It seems that there are no variants
        if variant_master_objectclass is None:
            logger.warning("It seems that there are no variants")
            return {}

        # Query the variant master to get all the features

        variant_master_layer = variant_master_objectclass.layers[0]
        query = variant_master_layer.query(
            where=search_expression, returnGeometry=False
        )
        # TODO Refactor
        variant_master_features = list(query.resolve())[0]["features"]

        variant_master_ids = [
            feature["attributes"]["ID"] for feature in variant_master_features
        ]

        # Query Variants in the Object using the id
        for variant_master_id in variant_master_ids:
            search_expression = "ID={}".format(variant_master_id)

            current_masters = variant_master_objectclass.query(where=search_expression)[
                1
            ]

            # We request all the variants pro master
            for current_master in current_masters:
                variant_list = current_master.variants(variant_master_id)

                # We sort all the variants. This help to build the variant because
                # the variant id will be always bigger
                sorted_variant = sorted(variant_list, key=lambda k: k["ID"])
                complete_list.extend(sorted_variant)

        # Crete the tree, this is the first node
        root_node = Node("0")

        for variant in complete_list:
            if variant["PARENT"] == -1:
                Node(
                    name=str(variant["ID"]),
                    id=variant["ID"],
                    variant_name=variant["NAME"],
                    parent=find_by_attr(root_node, "0"),
                    master=True,
                )
            else:
                Node(
                    name=str(variant["ID"]),
                    id=variant["ID"],
                    variant_name=variant["NAME"],
                    parent=find_by_attr(root_node, str(variant["PARENT"])),
                    master=False,
                )

        # This is the dictionary with the tree
        tree_exporter = DictExporter()
        logger.debug(tree_exporter.export(root_node))

        # This is the iterable with all the traversing structure
        # https://anytree.readthedocs.io/en/latest/api/anytree.iterators.html#anytree.iterators.preorderiter.PreOrderIter
        iterable_tree = PreOrderIter(root_node)

        logger.info("Variants tree %s:", RenderTree(root_node).by_attr("variant_name"))

        # Return the 2 items
        try:
            variant_tree = tree_exporter.export(root_node)[0]["children"]
        except KeyError:
            variant_tree = tree_exporter.export(root_node)
        return variant_tree, iterable_tree

    @property
    def has_variants(self):
        # type: () -> bool

        """
        Check if the project contains variants
        """

        variant_master_objectclass = next(
            (
                item
                for item in self.objectclasses
                if item.objectClassType == "VNTMASTER"
            ),
            None,
        )

        return variant_master_objectclass is not None

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
            raise EmsProjectException("Error talking with EMS")
        try:
            json_response = response.json()
        except ValueError as exception:
            logger.exception(
                "Response is not json. You are probably on the login website:%s",
                exception,
            )
        else:
            return json_response
