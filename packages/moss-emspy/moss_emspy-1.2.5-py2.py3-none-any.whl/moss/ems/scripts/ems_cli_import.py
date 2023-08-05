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
import os
import sys
from os import listdir, walk
from os.path import exists, isdir, isfile, join

from tqdm import tqdm

logger = logging.getLogger("ems_cli_import")


class EmsCliImport:
    def __init__(self):
        # when not used in CLI
        self.cli_mode = False

    def ems_import(self, project_name, input_directory):
        # type: (str, str) -> None
        """Imports a complete EMS project

        Args:
            project_name: the name of the EMS project
            input_directory:  the name of the input directory

        Returns:

        Raises:
            EmsCliException
        """
        from moss.ems.scripts.ems_cli import EmsCliException
        from moss.ems.utilities.sortutil import ObjectClassSorter

        logger.info("Starting import process")
        logger.debug(
            "Projects in the current instance: %s",
            self.ems_service.projects,  # type: ignore
        )

        # Check if the path exist
        if not os.path.exists(input_directory):
            logger.error("The path %s does not exist")
            sys.exit(1)

        project = next(
            iter(filter(lambda p: p.name == project_name, self.ems_service.projects)),  # type: ignore
            None,
        )

        # project = None
        if project is not None:
            logger.error(
                "The project '%s' does already exist in this instance", project_name
            )
            raise EmsCliException(
                "The project '{}' does already exist in this instance".format(
                    project_name
                )
            )

        # Get the project file (the json with the complete structure)
        saved_project = self.file2json(  # type: ignore
            os.path.join(input_directory, "project.json")  # type: ignore
        )
        if "description" not in saved_project:
            raise EmsCliException("The JSON structure in project.json is wrong")
        logger.debug(
            "Importing project %s:\n\tDescription: %s",
            project_name,
            saved_project["description"],
        )
        ret_value = self.ems_service.import_project(saved_project, project_name)  # type: ignore

        if ret_value is False:
            logger.error("The project '%s' couldn't be imported", project_name)
            raise EmsCliException(
                "The project '{}' couldn't be imported".format(project_name)
            )
        project = self.ems_service.project(project_name)  # type: ignore

        # Check if the project has variant
        sorter = ObjectClassSorter(project.objectclasses)
        objectclasses = sorter.by_reference()

        # Looking for the VNT Master Objectclass
        variant_master_found = None
        logger.info(
            "Looking for a VARIANTMASTER in the project structure ... i.e. a variant"
            " project"
        )
        variant_master_found = next(
            (item for item in objectclasses if item.objectClassType == "VNTMASTER"),
            None,  # type: ignore
        )

        # Check if there is a variant tree
        if variant_master_found is not None:
            logger.info(
                "The VARIANTMASTER '{}' was found".format(variant_master_found.name)
            )
            # switching to the VNTMASTER directory
            input_directory = join(input_directory, variant_master_found.name)
            # Get all the master variants ids, i.e. the directory names
            master_variant_ids = [
                mvi
                for mvi in listdir(input_directory)
                if isdir(join(input_directory, mvi))
            ]
            logger.info(
                "{} master variants were found: {}".format(
                    len(master_variant_ids), master_variant_ids
                )
            )

            # maps an objectclass to a map of old to new ids
            objectclass_map = {}

            # maps the old master id to a new master id
            master_map = {}
            objectclass_map[variant_master_found.name] = master_map

            total_master_count = len(master_variant_ids)

            if self.cli_mode:
                print("Found {n} masters. Start import...".format(n=total_master_count))

            with tqdm(total=total_master_count, disable=self.cli_mode is False) as pbar:
                while len(master_variant_ids) > 0:
                    current_variant_id = master_variant_ids.pop(0)

                    logger.info("Creating master variant {}".format(current_variant_id))
                    master_variant_dir = join(input_directory, current_variant_id)

                    if not os.path.exists(join(master_variant_dir, "master.json")):
                        raise EmsCliException(
                            "The file 'master.json' is missing in {}".format(
                                master_variant_dir
                            )
                        )
                    logger.info("Reading the master features in 'master.json'")
                    master_features = self.file2json(  # type: ignore
                        join(master_variant_dir, "master.json")
                    )
                    preferred_field_name = ""
                    preferred_variant = ""
                    preferred_field_exisits = False
                    preferred_field = next(
                        (
                            item
                            for item in variant_master_found.fields  # type: ignore
                            if item["type"] == "emsFieldTypeVariantPref"
                        ),
                        None,
                    )
                    selfref_field = next(
                        (
                            item
                            for item in variant_master_found.fields  # type: ignore
                            if item["type"] == "emsFieldTypeObjectClass"
                            and item["objectClassName"] == variant_master_found.name
                        ),
                        None,
                    )

                    if selfref_field is not None:
                        # variant master supports self reference
                        selfref_field_name = selfref_field["name"]
                        selfref_id = master_features["attributes"][selfref_field_name]

                        # if referenced master object is not created yet, push the current
                        # master_variant_id back to stack and continue with next folder
                        if selfref_id is not None and selfref_id not in master_map:
                            master_variant_ids.append(current_variant_id)
                            continue

                    if preferred_field is not None:
                        preferred_field_exisits = True
                        preferred_field_name = preferred_field["name"]
                        preferred_variant = master_features["attributes"][
                            preferred_field_name
                        ]
                        del master_features["attributes"][preferred_field_name]

                    old_master_id = master_features["attributes"]["ID"]

                    # theese attributes need to be deleted, otherwise -> error
                    del master_features["attributes"]["GLOBALID"]
                    del master_features["attributes"]["ID"]

                    # add the new master feature
                    logger.info("Add the new master features")
                    result_dict = variant_master_found.layers[0].add_features(
                        [master_features]
                    )
                    if "code" in result_dict:
                        error_dict = result_dict
                        raise EmsCliException(
                            "Could not add master variant features:\n\tCode:"
                            " {}\n\tMessage: {}\n\tDescription: {}".format(
                                error_dict["code"],
                                error_dict["message"],
                                error_dict["description"],
                            )
                        )
                    if "error" in result_dict["addResults"][0]:
                        error_dict = result_dict["addResults"][0]["error"]
                        raise EmsCliException(
                            "Could not add master variant features:\n\tCode:"
                            " {}\n\tMessage: {}\n\tDescription: {}".format(
                                error_dict["code"],
                                error_dict["message"],
                                error_dict["description"],
                            )
                        )
                    new_master_id = result_dict["addResults"][0]["objectId"]

                    master_map[old_master_id] = new_master_id

                    # the root variant(s) of the new feature, hopefully only one
                    all_variants = variant_master_found.variants(new_master_id)
                    if len(all_variants) > 1:  # type: ignore
                        raise EmsCliException("More than one root variant was found")
                    if not exists(join(master_variant_dir, "variants.json")):
                        raise EmsCliException(
                            "The file 'variants.json' is missing in {}".format(
                                master_variant_dir
                            )
                        )
                    # read the variants for the master feature
                    logger.info(
                        "Reading the variants for the master features in"
                        " 'variants.json'"
                    )
                    exported_variants = self.file2json(  # type: ignore
                        join(master_variant_dir, "variants.json")
                    )

                    root_variant = all_variants[0]

                    featureid_name, master_results = variant_master_found.query(
                        where="ID = " + str(new_master_id)
                    )
                    master = master_results[0]

                    # maps old variant ids to new variant ids
                    variant_map = {}

                    new_variant_id = root_variant["ID"]

                    for variant in exported_variants:
                        # is it the start variant ?
                        if variant["PARENT"] != -1:
                            # we need the master_id
                            new_parent_variant_id = variant_map[variant["PARENT"]]

                            logger.info(
                                "Derive '{}' from master_id {}, variant_id {}".format(
                                    variant["NAME"],
                                    new_master_id,
                                    new_parent_variant_id,
                                )
                            )

                            result_dict = master.derive(
                                feature_id=new_master_id,
                                variant_id=new_parent_variant_id,
                                name=variant["NAME"],
                                description=variant["DESCRIPTION"],
                                status=variant["STATUS"],
                                category=variant["CATEGORY"],
                            )

                            if "error" in result_dict["deriveVariantResult"]:
                                error_dict = result_dict["deriveVariantResult"][0][
                                    "error"
                                ]
                                raise EmsCliException(
                                    "Could not derive from master variant features:"
                                    "\n\tCode: {}\n\tMessage: {}\n\tDescription: {}"
                                    .format(
                                        error_dict["code"],
                                        error_dict["message"],
                                        error_dict["description"],
                                    )
                                )
                            # set the new id in the exported_variants tree to find parents
                            new_variant_id = result_dict["deriveVariantResult"][
                                "objectId"
                            ]

                            # now drain the variant, so we remove any derived objects from the new variant
                            master.drain(
                                feature_id=new_master_id,
                                variant_id=new_variant_id,
                                object_classes="*",
                            )

                        variant_map[variant["ID"]] = new_variant_id
                        variant_dir = join(master_variant_dir, str(variant["ID"]))

                        # now add the features, i.e. all the json files in the subdirectories (name=obj_class)
                        # (json file name = layer name)

                        for objectclass in objectclasses:
                            featureset_dir = join(variant_dir, objectclass.name)

                            if not isdir(featureset_dir):
                                continue
                            logger.info("Processing objectclass {}".format(objectclass))

                            # reset in each objectclass iteration
                            created_features = {}
                            failed_features = []
                            objectclass_map[objectclass.name] = created_features

                            # list of already existing feature IDs
                            old_feature_id = []

                            featureset_files = [
                                f
                                for f in listdir(featureset_dir)
                                if isfile(join(featureset_dir, f))
                            ]
                            for featureset_file in featureset_files:
                                # list of features to add
                                features_to_add = []
                                # list of features already created, which therefore must be updated
                                features_to_update = []

                                layer_name = featureset_file[
                                    0 : featureset_file.find(".json")
                                ]
                                logger.info(
                                    "Add layer {} to {}".format(
                                        layer_name, objectclass.name
                                    )
                                )
                                feature_set = self.file2json(  # type: ignore
                                    join(featureset_dir, featureset_file)
                                )

                                references = list(
                                    filter(
                                        lambda field: field["type"]
                                        == "emsFieldTypeObjectClass",
                                        objectclass.fields,
                                    )
                                )

                                for feature in feature_set:

                                    # get a reference to the old feature id
                                    old_feature_id.append(feature["attributes"]["ID"])
                                    # o_feature_id = feature["attributes"]["ID"]

                                    if old_feature_id[-1] in created_features:
                                        # already created so update the features ID
                                        new_feature_id = created_features[
                                            old_feature_id[-1]
                                        ]
                                        # n_feature_id = feature_id_map[old_feature_id]

                                        feature["attributes"]["ID"] = new_feature_id

                                        # and append it to the list of featurs to update
                                        features_to_update.append(feature)

                                    # only update the feature if it was created previously
                                    # without any errors.
                                    elif old_feature_id[-1] not in failed_features:
                                        # not yet created

                                        # The GLOBALID and ID can't be imported but most be
                                        # newly generated by the EMS
                                        del feature["attributes"]["GLOBALID"]
                                        del feature["attributes"]["ID"]
                                        for reference in references:
                                            reference_field = reference["name"]
                                            ref_obj = reference["objectClassName"]
                                            id_map = objectclass_map[ref_obj]
                                            old_id = feature["attributes"][
                                                reference_field
                                            ]
                                            new_id = id_map[old_id]
                                            feature["attributes"][
                                                reference_field
                                            ] = new_id

                                        del feature["variants"]
                                        features_to_add.append(feature)

                                # get acces to the layer by its feature_set
                                # layer = layer_from_feature_set(feature_set)
                                layer = objectclass.layer(layer_name)

                                if features_to_add:
                                    # add the not yet created features
                                    logger.info(
                                        "Add {} features to layer {} {}.".format(
                                            len(features_to_add),
                                            layer_name,
                                            featureset_dir,
                                        )
                                    )
                                    add_results = layer.add_features(
                                        features=features_to_add,
                                        variant_id=new_variant_id,
                                    )

                                    # and update the created_features map with the latest additions
                                    for idx, add_result in enumerate(
                                        add_results["addResults"]
                                    ):

                                        # since EMS garantuees that add_results are returned
                                        # in the same order as the list of added features
                                        # we can easily access the id of the created feature
                                        # in the old system

                                        added_feature = features_to_add[idx]

                                        if add_result["success"] is True:
                                            new_feature_id = add_result["objectId"]

                                            created_features[
                                                old_feature_id[idx]
                                            ] = new_feature_id
                                            # feature_id_map[o_feature_id] = new_feature_id
                                        else:
                                            logger.error(
                                                "Failed to create feature: %s",
                                                added_feature,
                                            )

                                if features_to_update:
                                    # update the already created features
                                    logger.info(
                                        "Update {} features in layer {}.".format(
                                            len(features_to_update), layer_name
                                        )
                                    )
                                    update_results = layer.update_features(
                                        features=features_to_update,
                                        variant_id=new_variant_id,
                                    )

                                    # and update the created_features map with the latest additions
                                    for idx, update_result in enumerate(
                                        update_results["updateResults"]
                                    ):
                                        if update_result["success"] is False:
                                            failed_features.append(
                                                features_to_update[idx]["attributes"][
                                                    "ID"
                                                ]
                                            )
                                            logger.error(
                                                """
                                                Failed to update feature. This means the feature was
                                                only created partialy:\n
                                                Feature-Set:\n
                                                %s\n
                                                Update Result:\n
                                                %s
                                                """,
                                                features_to_update,
                                                update_result,
                                            )

                    # Now lets restore the preferred variant ID
                    if preferred_field_exisits is True:
                        pagination_query = variant_master_found.layers[0].query(
                            where="ID={}".format(new_master_id)
                        )
                        result = list(pagination_query.resolve())[0]
                        features = result["features"]
                        feature_attributes = features[0]["attributes"]
                        try:
                            feature_attributes[preferred_field_name] = variant_map[
                                preferred_variant
                            ]
                        except KeyError:
                            logger.warning(
                                "The preferred variant %s does not exist",
                                preferred_variant,
                            )
                        result_dict = variant_master_found.layers[0].update_features(
                            features
                        )
                        if "code" in result_dict:
                            error_dict = result_dict
                            raise EmsCliException(
                                "Could not update master variant features:"
                                "\n\tCode: {}\n\tMessage: {}\n\tDescription: {}".format(
                                    error_dict["code"],
                                    error_dict["message"],
                                    error_dict["description"],
                                )
                            )
                        if "error" in result_dict["updateResults"][0]:
                            error_dict = result_dict["updateResults"][0]["error"]
                            raise EmsCliException(
                                "Could not update master variant features: "
                                "\n\tCode: {}\n\tMessage: {}\n\tDescription: {}".format(
                                    error_dict["code"],
                                    error_dict["message"],
                                    error_dict["description"],
                                )
                            )
                    pbar.update(1)

            if self.cli_mode:
                print("Import successfully finished.")
            # show the new tree
            project.variants_tree()
        else:
            objclass_name_marker = ""
            created_features = []
            failed_features = []
            for dirpath, _, filenames in walk(input_directory):
                for filename in [f for f in filenames if f.endswith("Layers.json")]:
                    # the object class name is the directory name of the JSON file
                    objclass_name = os.path.split(dirpath)[1]
                    logger.info("Processing Objectclass: %s", objclass_name)

                    # the add_feature and update_feature process is only
                    # necessary for one objectclass!
                    # Do we have a new object class?
                    if objclass_name != objclass_name_marker:
                        # new map to track which features where created
                        created_features = {}

                        # new map to track features for which creation failed
                        failed_features = []
                        objclass_name_marker = objclass_name

                    # list of features to add
                    features_to_add = []
                    # list of features already created, which therefore must be updated
                    features_to_update = []
                    # list of already existing feature IDs
                    old_feature_id = []

                    layers = self.file2json(os.path.join(dirpath, filename))  # type: ignore
                    layer_name = filename[0 : filename.find("_Layers.json")]

                    # split features into two lists: already created and not yet created
                    for feature in layers["features"]:

                        # get a reference to the old feature id
                        old_feature_id.append(feature["attributes"]["ID"])

                        if old_feature_id[-1] in created_features:
                            # already created so update the features ID
                            new_feature_id = created_features[old_feature_id[-1]]

                            feature["attributes"]["ID"] = new_feature_id

                            # and append it to the list of featurs to update
                            features_to_update.append(feature)

                        # only update the feature if it was created previously
                        # without any errors.
                        elif old_feature_id[-1] not in failed_features:
                            # not yet created

                            # The GLOBALID and ID can't be imported but most be
                            # newly generated by the EMS
                            del feature["attributes"]["GLOBALID"]
                            del feature["attributes"]["ID"]
                            features_to_add.append(feature)

                    # get acces to the layer by its feature_set
                    # layer = layer_from_feature_set(feature_set)
                    layer = project.objectclass(objclass_name).layer(layer_name)

                    if features_to_add:
                        # add the not yet created features
                        add_results = layer.add_features(features_to_add)

                        # and update the created_features map with the latest additions
                        for idx, add_result in enumerate(add_results["addResults"]):

                            # since EMS garantuees that add_results are returned
                            # in the same order as the list of added features
                            # we can easily access the id of the created feature
                            # in the old system

                            added_feature = features_to_add[idx]

                            if add_result["success"] is True:
                                new_feature_id = add_result["objectId"]

                                created_features[old_feature_id[idx]] = new_feature_id
                            else:
                                logger.error(
                                    "Failed to create feature: %sß", added_feature
                                )

                    if features_to_update:
                        # update the already created features
                        update_results = layer.update_features(features_to_update)

                        # and update the created_features map with the latest additions
                        for idx, update_result in enumerate(
                            update_results["updateResults"]
                        ):
                            if "error" in update_result:
                                failed_features.append(
                                    features_to_update[idx]["attributes"]["ID"]
                                )
                                logger.error(
                                    """
                                    Failed to update feature. This means the feature was
                                    only created partialy:\n
                                    Feature-Set:\n
                                    %s\n
                                    Update Result:\n
                                    %s
                                    """,
                                    features_to_update,
                                    update_result,
                                )
        logger.info("Import completed")
