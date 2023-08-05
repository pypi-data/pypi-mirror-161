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

logger = logging.getLogger(__file__)


class GeojsonConvertException(Exception):
    """
    Exception for the GeojsonConvert
    """


class GeojsonConverter:
    """
    The class to convert a GeoJSON to ESRI

    """

    @staticmethod
    def _convert_geometry(geometry):
        """
        Convert the geometry into the ESRI notation

        :param geometry: The GDAL geometry dict.
        :type geometry: dict
        :returns:  dictionary -- a dictionary depending on the type of geometry, i.e.
        Point, MultiPoint, Polygon, MultiPolygon, LineString, MultiLineString.
        :raises: GeojsonConvertException
        """

        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")

        if geometry_type is None:
            logger.error("Error in geojson defintion: %s", geometry)
            raise GeojsonConvertException

        # Point
        if geometry_type == "Point":
            try:
                point_x = coordinates[0]
                point_y = coordinates[1]
            except IndexError:
                logger.error("Invalid geometry definition: %s", coordinates)
                raise GeojsonConvertException
            else:
                return {"x": point_x, "y": point_y}

        # MultiPoint
        if geometry_type == "MultiPoint":
            all_points = []
            for point in coordinates:
                all_points += [point]
            return {"points": all_points}

        # Polygon
        if geometry_type == "Polygon":
            # logger.info("Polygon %s", coordinates)
            return {"rings": coordinates}
        # MultiPoygon
        if geometry_type == "MultiPolygon":
            # logger.info(coordinates)
            all_polygons = []
            for polygon in coordinates:
                all_polygons += polygon
            return {"rings": all_polygons}

        # LineString
        if geometry_type == "LineString":
            # logger.debug("Converting LineString %s", coordinates)
            return {"paths": [coordinates]}

        # MultiLineString
        if geometry_type == "MultiLineString":
            # logger.debug("Converting LineString %s", coordinates)
            all_lines = []
            for line in coordinates:
                all_lines += line
            return {"paths": [all_lines]}

        raise GeojsonConvertException("Unknown geometry type: %s" % geometry_type)

    @staticmethod
    def to_esri(feature):
        """
        Converts a GDAL feature to an ESRI feature

        :param feature: The feature dict containing "properties" and "geometry".
        :type feature: dict
        :returns:  dict -- an ESRI conform feature dictionary
        :raises: GeojsonConvertException
        """
        esri_output = {}

        # Attributes

        try:
            esri_output["attributes"] = feature["properties"]
        except KeyError:
            logger.debug("There is  no 'properties' key in the current feature.")
            esri_output["attributes"] = {}

        # Geometry
        try:
            geometry = feature["geometry"]
        except KeyError:
            logger.error("There is  no 'geometry' key in the current feature.")
            raise GeojsonConvertException
        else:
            esri_output["geometry"] = GeojsonConverter._convert_geometry(geometry)

        return esri_output
