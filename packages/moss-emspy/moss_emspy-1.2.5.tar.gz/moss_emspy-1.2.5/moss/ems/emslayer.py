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
import mimetypes
import os
import re
from typing import List, Optional

from requests import Response

from moss.ems.utilities import PaginationQuery

logger = logging.getLogger(__file__)


class EmsLayerException(Exception):
    """Exception for EmsLayer."""


class EmsLayer(object):
    """EmsLayer Class."""

    def __init__(self, name, object_class, project, session, definition=None):
        """Initialize the layer class.

        Args:
            name: the name of the layer
            object_class: an instance of an objectclass
            project: an instance of a project
            session: a session object
            definition: a definition of the layer

        Returns:

        Raises:

        """
        self.name = name
        self.object_class = object_class
        self.project = project

        self._session = session

        if definition is not None:
            self.definition = definition

    def query(
        self, output_format="json", where="1=1", variants=None, geometry=None, **kwargs
    ):
        """Run a paginated query on a layer

        Args:
            output_format: str: the supported output formats of the EMS query Rest call
            where: a SQL-like string
            geometry: am Esri Envelope used to filter the query
            variants: a list of variant IDs to query
            **kwargs: additional a keyworded, variable-length argument list
            please refer to ems documentation

        Returns:
            a pagination query object
        """

        url = "/".join(["rest", self.project, self.object_class, self.name, "query"])

        request_parameters = {"f": output_format, "where": where}

        if variants is not None:
            if isinstance(variants, list):
                variant_ids = ",".join([str(variant_id) for variant_id in variants])
                request_parameters["variants"] = variant_ids
            else:
                request_parameters["variants"] = variants

        #  To ensure compatibility with the old version
        #  In the old version geometry was a boolean to returnGeometry

        if type(geometry) == bool:
            request_parameters["returnGeometry"] = geometry
        else:
            if geometry is not None:
                request_parameters["geometry"] = geometry

        for key, item in kwargs.items():
            request_parameters[key] = item

        return PaginationQuery(self._session, url, self.project, **request_parameters)

    def add_features(self, features, variant_id=None):
        """Add features to a layer

        Args:
            features: a list of features
            variant_id:

        Returns:
            the response dict for the addFeatures request or None on error
        Raises:
            EmsLayerException
        """

        url = "/".join(
            ["rest", self.project, self.object_class, self.name, "addFeatures"]
        )

        if not isinstance(features, list):
            raise EmsLayerException("The features have to be of type 'list'.")

        post_data = {
            "f": "json",
            "features": json.dumps(features),
        }

        # Add the variant parameter if provided
        if variant_id is not None:
            logger.debug("Using variant: variant_id is %s ", variant_id)

            try:
                post_data["variant"] = int(variant_id)
            except TypeError:
                logger.error("The variant_id is not an integer")
                raise EmsLayerException("The variant_id is not an integer")

        logger.debug("Sending request data: %s", post_data)

        response = self._session.post(url, data=post_data)
        response_dict = response.json()

        logger.debug("add_feature: response %s", response_dict)
        error_flag = False

        # addResults could have more than one result sets
        try:
            for i in range(len(response_dict["addResults"])):
                if response_dict["addResults"][i]["success"] is False:
                    error_flag = True
                    error_dictionary = response_dict["addResults"][i]["error"]

                    logger.error("Message: %s", error_dictionary["message"])
                    logger.error("Description: %s", error_dictionary["description"])
                    logger.error("Code: %s", error_dictionary["code"])
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return error_dictionary

        if error_flag is True:
            logger.info("Not all the features were added successfully.")
        else:
            logger.info("All the features were added successfully.")
        logger.debug("Features:\n%s", json.dumps(features))
        return response_dict

    def update_features(self, features, variant_id=None):
        """Modifies the features of a layer

        Args:
            features: a list of features
            variant_id:

        Returns:
            the response dict for the updateFeatures request or None on error
        Raises:
            EmsLayerException
        """

        if not isinstance(features, list):
            raise EmsLayerException("The features have to be of type 'list'.")

        # firstly get which fields (via objectClass) are editable
        url = "/".join(["rest", self.project, "objectClasses"])
        request_parameters = {"f": "json"}

        response = self._session.get(url, params=request_parameters)
        response_dict = response.json()
        objectclass = next(
            iter(
                filter(
                    lambda x: x["name"] == self.object_class,
                    response_dict["objectClasses"],
                )
            ),
            None,
        )

        # avoid sending fields that are not editable.
        exclude_fields = []

        for field in objectclass["fields"]:
            if field["name"] != "ID":
                if not field["editable"]:
                    exclude_fields.append(field["name"])

        for feature in features:
            for attribute in list(feature["attributes"]):
                if attribute in exclude_fields:
                    feature["attributes"].pop(attribute, None)

        post_data = {
            "f": "json",
            "features": json.dumps(features),
        }
        # Add the variant parameter if provided
        if variant_id is not None:
            logger.debug("Using variant: variant_id is %s ", variant_id)

            try:
                post_data["variant"] = int(variant_id)
            except TypeError:
                logger.error("The variant_id is not an integer")
                raise EmsLayerException("The variant_id is not an integer")

        url = "/".join(
            ["rest", self.project, self.object_class, self.name, "updateFeatures"]
        )

        response = self._session.post(url, data=post_data)
        response_dict = response.json()
        error_flag = False

        # updateResults could have more than one result sets
        try:
            for i in range(len(response_dict["updateResults"])):
                if response_dict["updateResults"][i]["success"] is False:
                    error_flag = True
                    error_dictionary = response_dict["updateResults"][i]["error"]

                    logger.error("Message: %s", error_dictionary["message"])
                    logger.error("Description: %s", error_dictionary["description"])
                    logger.error("Code: %s", error_dictionary["code"])
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return error_dictionary

        if error_flag is True:
            logger.info("Not all the features were modified successfully.")
        else:
            logger.info("All the features were modified successfully.")
        return response_dict

    def delete_features(self, object_ids, where=None, variant_id=None):
        """Delete the features in the list of objectIds of a layer

        Args:
            object_ids: a list of object IDs to delete the features
            where: a SQL statement

        Returns:
            the response dict for the deleteFeatures request or None on error
        """

        url = "/".join(
            ["rest", self.project, self.object_class, self.name, "deleteFeatures"]
        )

        if isinstance(object_ids, list):
            ids = ",".join([str(object_id) for object_id in object_ids])
        else:
            ids = object_ids

        post_data = {"f": "json", "objectIds": ids}

        if where is not None:
            post_data["where"] = where

        # Add the variant parameter if provided
        if variant_id is not None:
            logger.debug("Using variant: variant_id is %s ", variant_id)

            try:
                post_data["variant"] = int(variant_id)
            except TypeError:
                logger.exception("The variant_id is not an integer")

        response = self._session.post(url, data=post_data)
        response_dict = response.json()
        error_flag = False

        try:
            # deleteResults could have more than one result set
            for i in range(len(response_dict["deleteResults"])):
                if response_dict["deleteResults"][i]["success"] is False:
                    error_flag = True
                    error_dictionary = response_dict["deleteResults"][i]["error"]

                    logger.error("Message: %s", error_dictionary["message"])
                    logger.error("Description: %s", error_dictionary["description"])
                    logger.error("Code: %s", error_dictionary["code"])
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return error_dictionary

        if error_flag is True:
            logger.info("Not all the features were deleted successfully.")
        else:
            logger.info("All the features were deleted successfully.")
        return response_dict

    def attachments(self, feature_id="1", asUrl=False, appType="master"):
        """
        This will list all the attachment infos for given feature.

        Args:

            feature_id (int): The id of the feature
            asUrl (bool): Return the storage path of the attachment. Using this
                          option is a security risk!
            appType (str): archive/preview/maste(default)
        """

        url = "/".join(
            [
                "rest",
                self.project,
                self.object_class,
                self.name,
                str(feature_id),
                "attachments",
            ]
        )
        get_params = {"f": "json", "asUrl": asUrl, "appType": appType}
        response = self._session.get(url, params=get_params)
        response_dict = response.json()

        logger.debug(response_dict)

        logger.info("Successfully queried the attachments.")
        return response_dict

    def add_attachment(self, feature_id, app_type="master", file_path=""):
        """Adds an attachment to a layer/feature

        not officially supported yet
        """

        url = "/".join(
            [
                "rest",
                self.project,
                self.object_class,
                self.name,
                str(feature_id),
                "addAttachment",
            ]
        )

        # absolute path
        upload_file = os.path.abspath(file_path)
        file_name = os.path.basename(upload_file)

        if not os.path.exists(file_path):
            raise EmsLayerException("The path {} does not exist".format(upload_file))

        files = {"attachment": (file_name, open(upload_file, "rb"))}

        post_data = {"f": "json", "apptype": app_type}
        response_dict = self._session.post(url, files=files, data=post_data).json()

        # results could have more than one result set
        try:
            if response_dict["addAttachmentResult"]["success"] is False:
                error_dictionary = response_dict["addAttachmentResult"]["error"]

                logger.error("Message: %s", error_dictionary["message"])
                logger.error("Description: %s", error_dictionary["description"])
                logger.error("Code: %s", error_dictionary["code"])
                return None
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return None

        logger.info("The attachment was added successfully.")
        return response_dict

    def update_attachment(self, feature_id, attachment_id, file_path):
        #  type: (int, int, str) -> bool
        """
        Update an attachment with a new one that will be uploaded

        Args:
            feature_id (int): The ID of the feature with attachment
            attachment_id (int): The ID of the attachment to be updated
            file_path (str): The Path to the new attachment file

        Returns:
            status (bool): The Status of the operation
        """

        url = "/".join(
            [
                "rest",
                self.project,
                self.object_class,
                self.name,
                str(feature_id),
                "updateAttachment",
            ]
        )

        # absolute path
        upload_file = os.path.abspath(file_path)
        file_name = os.path.basename(upload_file)

        if not os.path.exists(file_path):
            raise EmsLayerException("The path {} does not exist".format(upload_file))

        files = {"attachment": (file_name, open(upload_file, "rb"))}

        post_data = {"f": "json", "attachmentId": attachment_id}
        response_dict = self._session.post(url, files=files, data=post_data).json()

        # results could have more than one result set
        try:
            if response_dict["updateAttachmentResult"]["success"] is False:
                error_dictionary = response_dict["updateAttachmentResult"]["error"]

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

        logger.info("The attachment was updated successfully.")
        return True

    def register_attachment(
        self,
        feature_id,
        app_type="master",
        file_path="",
        fixed_path=True,
        content_type=None,
    ):
        """
        Registers an attachment without uploading a file.
        This function is used when attachments are already in the right place.
        This can e.g. be the case with a migration. Please note that the entry
        must be an absolute path

        Args:
            feature_id (int): The ID of the feature owning the attachment
            app_type (str): The apptype archive or master
            file_path (str): The path of the file to register
            fixed_path (bool): If True the base_path path is not prefixed.
            content_type (str): The Content type of the file.

        Returns:
            bool: The result of the register attachment
        """
        logger.info("Registering attachment.")

        url = "/".join(
            [
                "rest",
                self.project,
                self.object_class,
                self.name,
                feature_id,
                "registerAttachment",
            ]
        )
        register_file = os.path.abspath(file_path)
        logger.debug("File path is {0}".format(register_file))

        if not os.path.exists(file_path):
            raise EmsLayerException("The path {} does not exist".format(register_file))

        file_size = os.path.getsize(register_file)
        logger.debug("File size is {0}".format(file_size))

        # Guess mimetype if not defined
        if app_type is None:
            app_type = mimetypes.guess_type(register_file)[0]
        logger.debug("Detected mimetype is {0}".format(app_type))
        # If the mimetype is still none, raise an error
        if app_type is None:
            raise EmsLayerException("Can not detect mimetype, please specify it.")

        post_data = {
            "f": "json",
            "apptype": app_type,
            "filePath": file_path,
            "fixedPath": fixed_path,
            "contentType": content_type,
            "size": file_size,
        }
        logger.debug("Post data {0}".format(post_data))
        response_dict = self._session.post(url, data=post_data).json()

        # results could have more than one result set
        try:
            if response_dict["addAttachmentResult"]["success"] is False:
                error_dictionary = response_dict["addAttachmentResult"]["error"]

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

        logger.info("The attachment was registered successfully.")
        return True

    def delete_attachment(self, feature_id, attachment_ids):
        #  type: (int, List[int]) -> bool
        """
        Enables the deletion of several existing files or ZIP archives of a feature.

        Args:
            feature_id (int): The ID of the feature
            attachments_id (list): The list of attachments id to delete

        Return:
            result (bool): If the operation war succesfull
        """

        if type(attachment_ids) is list:
            attachments_list = ",".join(
                [str(attachment_id) for attachment_id in attachment_ids]
            )
            logger.debug("Deleting {0}".format(attachments_list))
        else:
            raise EmsLayerException("The attachments id should be a list of int")

        url = "/".join(
            [
                "rest",
                self.project,
                self.object_class,
                self.name,
                str(feature_id),
                "deleteAttachment",
            ]
        )

        post_data = {"f": "json", "attachmentIds": attachments_list}
        response_dict = self._session.post(url, data=post_data).json()

        # results could have more than one result set
        try:
            for attachment in response_dict["deleteAttachmentResult"]:
                if attachment["success"] is False:
                    error_dictionary = response_dict["deleteAttachmentResult"]["error"]

                    logger.error("Message: %s", error_dictionary["message"])
                    logger.error("Description: %s", error_dictionary["description"])
                    logger.error("Code: %s", error_dictionary["code"])
                    return False
                else:
                    logger.info(
                        "The attachment '%s' was deleted successfully.",
                        attachment["objectId"],
                    )
        except KeyError:
            error_dictionary = response_dict["error"]
            logger.error("Message: %s", error_dictionary["message"])
            logger.error("Description: %s", error_dictionary["description"])
            logger.error("Code: %s", error_dictionary["code"])
            return False

        if len(response_dict["deleteAttachmentResult"]) == 1:
            logger.info("The attachment was deleted successfully.")
        else:
            logger.info("The attachments were deleted successfully.")
        return True

    def download_attachment(self, feature_id, attachment_id, output_path=None):
        # type: (int, int, Optional[str]) -> bool
        """
        Download the specified attachment

        Args:
            feature_id (int): The ID of the feature owning the attachment
            attachment_id (int): The attachments ID
            output_path (str): Output directory where the attachment will be saved
        Returns:
            bool: The result of the download attachment
        """

        logger.info(
            "Downloading attachment {0} for feature {1}".format(
                attachment_id, feature_id
            )
        )

        url = "/".join(
            [
                "rest",
                self.project,
                self.object_class,
                self.name,
                str(feature_id),
                "attachments",
                str(attachment_id),
            ]
        )

        response = self._session.get(url)  # type: Response
        content_type = response.headers.get("Content-Type")  # type: Optional[str]
        if "application/json" not in content_type:
            logger.info("Headers {0}".format(response.headers))

            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition:
                filename = re.findall("filename=(.+)", content_disposition)[0]
            else:
                filename = "no_name"
            logger.info("Saving attachment to {0}".format(filename))

            if output_path:
                if not os.path.exists(output_path):
                    logger.error("The path {0} does not exist".format(output_path))
                    return False

                attachment_path = os.path.join(output_path, filename)

            else:
                attachment_path = filename

            logger.debug("Saving attachment to {0}".format(attachment_path))
            with open(attachment_path, "wb") as output_file:
                output_file.write(response.content)
            return True
        else:
            logger.error("The attachment url {0} does not exist".format(url))
            return False

    def __repr__(self):
        return self.name
