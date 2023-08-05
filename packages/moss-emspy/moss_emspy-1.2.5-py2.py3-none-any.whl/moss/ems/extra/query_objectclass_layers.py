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
"""
This module provides a utilty function to query all layer of an objectclass.
"""


def map_layers(layer):
    layer_dict = dict()

    layer_dict["name"] = layer.name
    layer_dict["type"] = layer.definition["type"]
    layer_dict["geometryType"] = layer.definition["geometryType"]

    return layer_dict


def query_objectclass_layers(
    objectclass, where="1=1", returnGeometry=True, variants=None, **kwargs
):

    """
    A utility function to query all layers of an objectclass.

    Example
    -------

    >>> feature_set = query_objectclass_layers(objectclass)
    >>> print(feature_set)

    Outputs the following structure:

        {
        count: int                          // The count of returned features
        objectIdFieldName: str              // The name of the objectclass id field
        fields: Field[]                     // The objectclass fields
        features: EmsFeature[]              // The features
        name: str                           // Name of the objectclass.
        spatialReference: SpatialReferece   // The srs of the objectclass.
        }

    Args:
        objectclass: EmsObjectclass: the objectclass instance to query.
        where: a SQL-like string
        geometry: a boolean to indicate to return also the geometry
        variants: a list of variant IDs to query
        **kwargs: additional a keyworded, variable-length argument list, please refer
            to ems documentation

    Returns:

        an aggregate result set, which contains the results of all layers of the queried
        objectclass.


    """

    layer_feature_sets = list()

    for layer in objectclass.layers:
        query = layer.query(
            where=where, variants=variants, geometry=returnGeometry, **kwargs
        )

        layer_feature_set = None

        for result in query.resolve():
            if layer_feature_set is None:
                layer_feature_set = result
            else:
                layer_feature_set["features"].append(result["features"])

        if layer_feature_set is not None:
            layer_feature_set["layer"] = layer
            layer_feature_sets.append(layer_feature_set)

    feature_map = dict()

    for layer_feature_set in layer_feature_sets:
        layer = layer_feature_set["layer"]

        for feature in layer_feature_set["features"]:
            feature_id = feature["attributes"]["ID"]

            if feature_map.get(feature_id) is None:
                feature_map[feature_id] = dict()
                feature_map[feature_id]["geometries"] = dict()
                feature_map[feature_id]["attributes"] = feature["attributes"]
                if "variants" in feature:
                    feature_map[feature_id]["variants"] = feature["variants"]

            feature_map[feature_id]["geometries"][layer.name] = (
                feature["geometry"] if "geometry" in feature else None
            )

    feature_set = dict()
    feature_set["count"] = len(feature_map)
    feature_set["objectIdFieldName"] = layer_feature_sets[0]["objectIdFieldName"]
    feature_set["spatialReference"] = layer_feature_sets[0]["spatialReference"]
    feature_set["fields"] = objectclass.fields
    feature_set["name"] = objectclass.name
    feature_set["features"] = list(feature_map.values())
    feature_set["layers"] = list(map(map_layers, objectclass.layers))

    return feature_set
