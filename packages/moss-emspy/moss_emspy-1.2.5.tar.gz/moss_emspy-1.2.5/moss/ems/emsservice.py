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


import base64
import json
import logging

import requests

from .emsproject import EmsProject
from .utilities import SessionBaseUrl

logger = logging.getLogger("ems_service")


__version__ = "2.0.0rc1"


class EmsServiceException(Exception):
    """
    Handles general exceptions for the service
    """


class EmsServiceAuthException(Exception):
    """
    Handles error related to authentication. For example
    an expired token.
    """


class Service(object):
    """
    A Class used to represent an EMS Service.

    To access a WEGA-EMS Service without authentication:

    Example:
        >>> my_service = Service("http://localhost:8080/wega-ems/")
        >>> my_service.projects
        ["project1", "project2"]

    If the service uses authentication, username and password can be provided
    as additional parameters:

    Example:
        >>> my_service = Service("http://localhost:8080/wega-ems/",
                username="Test",
                password="Test")
        >>> my_service.projects
        ["project1", "project2"]

    If working wih token, you can easily ignore the username and password:

    Example:
        >>> my_service = Service("http://localhost:8080/wega-ems/",
                                token="aabbcc")
        >>> my_service.projects
        ["project1", "project2"]

    Emspy uses requests Session so the session will remain active until close()
    is called.This will perform also a logout on Tomcat.

    Args:

        url (str):      The url to the WEGA-EMS instance service.
        username (str, optional): The username used for authentication.
        password (str, optional): The password used for authentication.
        token (str, optional): The token used for authentication
    """

    def __init__(self, base_url, username=None, password=None, token=None):
        # type: (str, str, str, str) -> None
        self.base_url = base_url
        self.username = username
        self.password = password

        if not self._url_is_correct():
            logger.error("The provided url is probably wrong.")
            raise EmsServiceException("The provided url is probably wrong.")

        # Create the session used to run the API call
        self.session = SessionBaseUrl(base_url)

        # Check if the service is secured. If so we need a username
        # and a password.
        if self._service_is_secured():
            logger.debug("The service is secured.")
            if token is not None:
                logger.debug("Using token %s", token)
                bearer_token = base64.urlsafe_b64encode(token.encode()).decode("utf-8")
                bearer_string = "Bearer {}".format(bearer_token)
                self.session.headers.update({"Authorization": bearer_string})
            else:
                if self.username:
                    if not self._login_user():
                        raise EmsServiceException("Wrong credentials provided.")

                else:
                    logger.error("The service is secured and there is no token.")
                    raise EmsServiceException(
                        "The service is secured. You need to provide a token."
                    )

        self._parameters = self._get_parameters()

    def _login_user(self):
        """
        This is the internal function to log in.
        """

        url = "login.xhtml"

        logger.debug("Logging user using the address %s", url)
        payload = {"username": self.username, "password": self.password}
        self.session.post(url, data=payload)

        # Test if we can read the projects. Just to see if the log is ok.
        # If the password is wrong, the code is always 200.

        url = "/".join(["rest", "info"])
        parameters = {"f": "json"}

        response = self.session.get(url, params=parameters)

        if response.status_code == 200:
            try:
                response_dict = json.loads(response.text)
            except ValueError as exception:
                logging.error(
                    "Login error. Please check username and password: %s", exception
                )
                return False
            else:
                self.information = response_dict
                return True
        else:
            raise EmsServiceException("Error logging in")

    def _get_parameters(self):
        """
        This will get the parameters of the current Project
        """
        url = "/".join(["rest", "projects"])
        parameters = {"f": "json"}

        response_dict = self._ems_request(url, parameters)

        return response_dict

    def _url_is_correct(self):
        """
        Check if the url is correct
        """
        url = "/".join([self.base_url, "rest"])

        if "jsessionid" in url:
            url = url.split(";")[0]
        try:
            response = requests.get(url)
        except (ValueError, requests.exceptions.ConnectionError) as exception:
            logging.error(
                "Error connecting to EMS Service for URL Testing: %s", exception
            )
            return False
        else:
            return response.status_code == 200 or response.status_code == 400

    def _service_is_secured(self):
        """
        This one wil return true if the service can be used
        without token or username/password
        """
        url = "/".join(["rest", "projects"])
        parameters = {"f": "json"}

        logging.debug("Checking if service at %s is secured", url)

        response = self.session.get(url, params=parameters)
        logging.debug(" Status code: %s", response.status_code)

        if "application/json" in response.headers["Content-Type"]:
            logging.info("The service needs no authentication.")
            return False

        return True

    @property
    def info(self):
        """
        List of all projects with some meta data.

        Examples:

            >>> my_service = Service("http://localhost:8080/wega-ems/")
            >>> my_service.info

        Returns:
            list: A list of projects and meta data for the current service
        """
        url = "/".join(["rest", "info"])
        parameters = {"f": "json"}

        information = self._ems_request(url, parameters)

        return information

    @property
    def configuration(self):
        """
        Return the base configuration of an administration client.

        Returns:
            a configuration dictionary containing a
            success property and version
        """
        url = "/".join(["rest", "configuration"])
        request_parameters = {"f": "json"}

        response_dict = self._ems_request(url, request_parameters)

        logger.info("Configuration loaded successfully for the service")
        return response_dict

    @property
    def projects(self):
        """
        The list of all the projects in the current Service.

        Example:

            >>> my_service = Service("http://localhost:8080/wega-ems/")
            >>> my_service.projects
            ['project1', 'project2']

        Returns:
           list: A list of `EmsProject`
        """
        url = "/".join(["rest", "projects"])
        parameters = {"f": "json"}

        response = self._ems_request(url, parameters)
        try:
            projects = response["projects"]
        except KeyError:  # pragma: no cover
            logger.debug("Getting projects %s", response)
            raise EmsServiceException("There is no projects key in response")
        return [EmsProject(self.session, project) for project in projects]

    def add_project(self, project_name, description=""):
        """
        Add a new Project to the current Service.

        Args:
            project_name (str): The project name
            description (str, optional): The project description.
            If not provided it will be an empty string.

        Example:
            >>> my_service = Service("http://localhost:8080/wega-ems/")
            >>> my_service.add_project("PROJECT", "Beschreibung")

        Returns
            The `EmsProject` instance of the added project
            or None in case of error
        """
        logger.debug("Trying to add the project '" + project_name + "'.")

        url = "/".join(["rest", "addProject"])
        request_parameters = {
            "f": "json",
            "name": project_name,
            "description": description,
        }

        response_dict = self._ems_request(url, request_parameters, "POST")

        try:
            if response_dict["addProjectResult"]["success"] is False:
                error_dictionary = response_dict["addProjectResult"]["error"]

                logger.error("Message: %s", error_dictionary["message"])
                logger.error("Description: %s", error_dictionary["description"])
                logger.error("Code: %s", error_dictionary["code"])
                return None
        except KeyError:  # pragma: no cover
            logger.error(
                "add_project delivered an unexpected response: %s", response_dict
            )
            raise EmsServiceException(
                "add_project delivered an unexpected response: %s", response_dict
            )

        logger.info("Added successfully the project '" + project_name + "'.")
        project = self.project(project_name)
        return project

    def delete_project(self, project_name):
        """
        Deletes the provided project. This operation can not be undone.

        Args:
            project_name (str): Project name

        Examples:

            >>> my_service = Service("http://localhost:8080/wega-ems/")
            >>> my_service.delete_project("PROJECT")

        Returns:
            bool: `True` or `False` if the project deleted successfully.

        """
        projects = self.projects

        # Choose the project
        project = next(iter(filter(lambda p: p.name == project_name, projects)), None)

        if project is None:
            logging.error(
                "The project %s does not exist in this instance", project_name
            )
            raise EmsServiceException(
                "The project %s does not exist in this instance" % project_name
            )

        project_id = project.id  # type: ignore

        # Send request
        url = "/".join(["rest", "deleteProject"])
        request_parameters = {"f": "json", "projectId": project_id}

        response_dict = self._ems_request(url, request_parameters, "POST")

        try:
            if response_dict["deleteProjectResult"]["success"] is False:
                logger.error(
                    "Message: %s",
                    response_dict["deleteProjectResult"]["error"]["message"],
                )
                logger.error(
                    "Description: %s",
                    response_dict["deleteProjectResult"]["error"]["description"],
                )
                logger.error(
                    "Code: %s", response_dict["deleteProjectResult"]["error"]["code"]
                )
                return False
        except KeyError:  # pragma: no cover
            logger.error(
                "delete_project delivered an unexpected response: %s", response_dict
            )
            raise EmsServiceException(
                "delete_project delivered an unexpected response: %s", response_dict
            )

        logger.info("Deleted successfully the project")
        return True

    def project(self, project_name):
        """
        Returns a project class by the project name.

        Example:
            >>> my_service.project("prj1")

        Args:
            project_name: The name of the project

        Returns:
            :obj:`EmsProject`
            or None if the project could not be found
        """

        projects = self.projects

        project = next(iter(filter(lambda p: p.name == project_name, projects)), None)

        if project is not None:
            return project

        else:
            logging.error(
                "The project %s does not exist in this instance", project_name
            )

    def export_project(self, project_name):
        """
        Exports the provided project

        Example:
            >>> my_service.export_project("prj1")

        Args:
            project_name: The name of the project to be exported

        Returns:
            :dict: Exported project information
        """
        logger.info("Starting the export of the project structure.")

        url = "/".join(["rest", project_name, "saveProject"])
        logger.debug("Export project %s", url)

        request_parameters = {
            "f": "json",
        }
        response_dict = self._ems_request(url, request_parameters, "POST")

        logger.debug("Project structure exported %s", response_dict)

        return response_dict

    def import_project(
        self,
        project_definition,
        project_name,
        password=None,
    ):
        """
        Import a project using the provided dict

        Example:
            >>> my_service.import_project("prj1")

        Args:
            project_definition (dict): The name of the project to be imported
            project_name       (str): The name of the project
            password           (str): The password

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        url = "/".join(["rest", "loadProject"])

        files = {
            "projectFile": (
                "loaded_project.json",
                json.dumps(project_definition),
                "application/json",
            ),
            "name": (None, project_name),
        }

        if password is not None:
            files["password"] = (None, password)

        response = self.session.post(url, files=files)
        response_dict = response.json()
        logger.debug("Response from import %s", response_dict)

        result = response_dict.get("loadProjectResult")

        if result is not None:
            if result["success"] is True:
                logger.info("Imported the project structure successfully.")
                return True
            else:
                logger.error("An error occured while importing the project structure!")
                logger.error("Message: %s", result["error"]["message"])
                logger.error("Description: %s", result["error"]["description"])
                logger.error("Code: %s", result["error"]["code"])
                return False
        else:
            logger.error(
                "Error loading project: %s", response_dict["loadProjectResult"]["error"]
            )
            return False

    def _ems_request(self, url, parameters, method="GET"):
        """Return a json response from a session"""
        logger.debug("New request to %s parameters %s", url, parameters)

        if method == "POST":
            response = self.session.post(url, data=parameters, allow_redirects=False)
        else:
            response = self.session.get(url, params=parameters, allow_redirects=False)

        # Handle redirect to login page

        if response.status_code == 302:
            raise EmsServiceAuthException("Invalid token provided")

        if response.status_code != 200:  # pragma: no cover
            logger.error(
                "Response is %s. Url: %s Parameters:%s Status code: %s",
                response.status_code,
                url,
                parameters,
                response.status_code,
            )
            raise EmsServiceException(
                "Communication error with EMS"
            )  # pragma: no cover
        try:
            json_response = response.json()
        except ValueError as exception:  # pragma: no cover
            logger.exception(
                "Response is not json. You are probablyon the login website:%s",
                exception,
            )
        else:
            return json_response

    def close(self):
        """
        Close the session to the service.
        """
        logout_url = "/".join([self.base_url, "logout.xhtml"])
        response = self.session.get(logout_url)
        if response.ok:
            logger.info("Session closed.")
        else:
            logger.warn("Error logging out using url %s", logout_url)
        self.session.close()
        logger.info("Session closed.")
