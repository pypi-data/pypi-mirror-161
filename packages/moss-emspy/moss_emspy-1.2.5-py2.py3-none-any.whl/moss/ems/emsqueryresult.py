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

LOGGER = logging.getLogger(__file__)


class EmsQueryResult:
    """
    The result of an EMS query
    """

    def __init__(self, session, project_name, objectclass_name, *args):

        self._session = session
        self._project = project_name
        self._objectclass_name = objectclass_name
        self._id = 0

        for key, value in args[0].items():
            # setattr(self, key.lower(), value)   Warum lower()?
            setattr(self, key, value)

    def variants(self, feature_id):
        """Return all the variants for a given feature ID

        Args:
            feature_id: The feature ID to get the variants for

        Returns:
            variants: a list of all variants or None
        """
        url = "/".join(
            ["rest", self._project, self._objectclass_name, str(feature_id), "variants"]
        )
        parameters = {"f": "json"}

        LOGGER.debug("Getting variants from %s", url)

        response = self._session.get(url, params=parameters)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        LOGGER.debug(response_dict)
        try:
            variants = response_dict["variants"]
            return variants
        except KeyError:
            error_dictionary = response_dict["error"]
            LOGGER.error("Message: %s", error_dictionary["message"])
            LOGGER.error("Description: %s", error_dictionary["description"])
            LOGGER.error("Code: %s", error_dictionary["code"])
            return None
        else:
            return None

    def derive(self, feature_id, variant_id, name, description, status=0, category=0):
        """Derive a new variant from an existing variant

        Args:
            feature_id: The feature ID of the existing vaiant
            variant_id: The variant ID of the existing vaiant
            name: The new variant name
            description: The new description
            status: the new status
            category: the new category

        Returns:
            response_dict: the response dict to the derive request or None
        """

        url = "/".join(
            [
                "rest",
                self._project,
                self._objectclass_name,
                str(feature_id),
                "variant",
                str(variant_id),
                "derive",
            ]
        )
        parameters = {
            "f": "json",
            "name": name,
            "description": description,
            "status": status,
            "category": category,
        }
        response = self._session.post(url, data=parameters)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        try:
            if response_dict["deriveVariantResult"]["success"] is False:
                error_dictionary = response_dict["deriveVariantResult"]["error"]

                LOGGER.error("Message: %s", error_dictionary["message"])
                LOGGER.error("Description: %s", error_dictionary["description"])
                LOGGER.error("Code: %s", error_dictionary["code"])
                return None
        except KeyError:
            error_dictionary = response_dict["error"]
            LOGGER.error("Message: %s", error_dictionary["message"])
            LOGGER.error("Description: %s", error_dictionary["description"])
            LOGGER.error("Code: %s", error_dictionary["code"])
            return None

        LOGGER.info(
            "Successfully derived new variant '%s' from '%s'",
            response_dict["deriveVariantResult"]["objectId"],
            feature_id,
        )
        return response_dict

    def delete(self, feature_id, variant_id):
        """Delete a variant

        Args:
            feature_id: The feature ID of the existing variant
            variant_id: The variant ID of the existing variant

        Returns:
            response_dict: the response dict to the delete request or None
        """
        url = "/".join(
            [
                "rest",
                self._project,
                self._objectclass_name,
                str(feature_id),
                "variant",
                str(variant_id),
                "delete",
            ]
        )
        parameters = {"f": "json"}
        response = self._session.post(url, data=parameters)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        try:
            if response_dict["deleteVariantResult"]["success"] is False:
                error_dictionary = response_dict["deleteVariantResult"]["error"]
                LOGGER.error("Message: %s", error_dictionary["message"])
                LOGGER.error("Description: %s", error_dictionary["description"])
                LOGGER.error("Code: %s", error_dictionary["code"])
                return False
        except KeyError:
            error_dictionary = response_dict["error"]
            LOGGER.error("Message: %s", error_dictionary["message"])
            LOGGER.error("Description: %s", error_dictionary["description"])
            LOGGER.error("Code: %s", error_dictionary["code"])
            return False

        LOGGER.info(
            "Successfully deleted variant '%s' from '%s'.",
            str(feature_id),
            str(variant_id),
        )
        return True

    def drain(self, feature_id, variant_id, object_classes):
        """Drains a variant from a list of object classes

        Args:
            feature_id: The feature ID to drain from
            variant_id: The variant ID to drain from
            object_classes: A list of objectclasses to drain from

        Returns:
            response_dict: the response dict to the drain request or None
        """

        url = "/".join(
            [
                "rest",
                self._project,
                self._objectclass_name,
                str(feature_id),
                "variant",
                str(variant_id),
                "drain",
            ]
        )
        parameters = {"f": "json", "objectClasses": object_classes}
        response = self._session.post(url, data=parameters)
        try:
            response_dict = response.json()
        except KeyError:
            return None

        try:
            if response_dict["drainVariantResult"]["success"] is False:
                error_dictionary = response_dict["drainVariantResult"]["error"]
                LOGGER.error("Message: %s", error_dictionary["message"])
                LOGGER.error("Description: %s", error_dictionary["description"])
                LOGGER.error("Code: %s", error_dictionary["code"])
                return False
        except KeyError:
            error_dictionary = response_dict["error"]
            LOGGER.error("Message: %s", error_dictionary["message"])
            LOGGER.error("Description: %s", error_dictionary["description"])
            LOGGER.error("Code: %s", error_dictionary["code"])
            return False

        LOGGER.info(
            "Successfully drained variant '%s' from object classes (%s).",
            response_dict["drainVariantResult"]["objectId"],
            object_classes,
        )
        return True
