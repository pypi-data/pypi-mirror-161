# -*- coding: utf-8 -*-
#
# Copyright (c) 2020  by M.O.S.S. Computer Grafik Systeme GmbH
#                         Hohenbrunner Weg 13
#                         D-82024 Taufkirchen
#                         http://www.moss.de#

import logging
import os
from os.path import join

from tqdm import tqdm

from moss.ems.utilities.pagination_query import EmsPaginationQueryException

logger = logging.getLogger("ems_cli_export")


class EmsCliExport:
    def __init__(self):
        # when not used in CLI
        self.cli_mode = False

    def ems_export(self, project_name, output_directory, indent, **kwargs):
        """
        Exports a complete EMS project

        Args:
            project_name (str): the name of the EMS project
            output_directory (str):  the name of the output directory

        Returns:

        Raises:
            EmsCliException
        """
        from moss.ems.scripts.ems_cli import EmsCliException

        # Check if the project exist
        project = self.ems_service.project(project_name)  # type: ignore

        if project is None:
            logger.error(
                "The project '%s' does not exist in this instance", project_name
            )
            raise EmsCliException(
                "The project '{}' does not exist in this instance".format(project_name)
            )

        # Export the project structure and save it to file
        saved_project = self.ems_service.export_project(project_name)  # type: ignore
        if "error" in saved_project:
            raise EmsCliException(
                "An error occured in exporting the project {}".format(project_name)
            )
        self.json_to_file(
            saved_project, output_directory, "project", indent
        )  # type: ignore

        # Check if the project has variant
        objectclasses = project.objectclasses
        # Looking for the VNT Master Objectclass
        variant_master_found = None
        variant_master_found = next(
            (item for item in objectclasses if item.objectClassType == "VNTMASTER"),
            None,
        )

        if variant_master_found is not None:
            logger.info(
                "An objectclass 'VNTMASTER' found. Switching to 'variant' mode!"
            )

            vn = variant_master_found.name
            subdir = join(output_directory, vn)
            os.mkdir(subdir)

            if "master_filter" in kwargs:
                master_filter = kwargs.get("master_filter")
                logger.info("Using {} to query master".format(master_filter))
                try:
                    query_results = variant_master_found.layers[0].query(
                        where=master_filter
                    )
                except EmsPaginationQueryException:
                    logger.error(
                        "Error running query with filter '{}'".format(master_filter)
                    )
                    return
            else:
                query_results = variant_master_found.layers[0].query()

            resolved_query = list(query_results.resolve())

            featureid_name = resolved_query[0]["objectIdFieldName"]
            features = resolved_query[0]["features"]

            if self.cli_mode:
                print("Found {n} masters. Start export...".format(n=len(features)))
            with tqdm(total=len(features), disable=self.cli_mode is False) as pbar:
                for query in features:
                    featureid = query["attributes"][featureid_name]
                    subdir = os.path.join(output_directory, vn, str(featureid))
                    logger.info("Creating master feature {}".format(featureid))
                    os.mkdir(subdir)
                    self.json_to_file(query, subdir, "master", indent)
                    variants = variant_master_found.variants(featureid)
                    self.json_to_file(variants, subdir, "variants", indent)
                    for variant in variants:
                        _id = variant[featureid_name]
                        subdir = os.path.join(
                            output_directory, vn, str(featureid), str(_id)
                        )
                        logger.info("Creating variant {}".format(_id))
                        os.mkdir(subdir)
                        for objectclass in objectclasses:
                            if objectclass.has_variant:
                                subdir = os.path.join(
                                    output_directory,
                                    vn,
                                    str(featureid),
                                    str(_id),
                                    objectclass.name,
                                )
                                logger.info(
                                    "Creating objectclass {}".format(objectclass.name)
                                )
                                os.mkdir(subdir)
                                for layer in objectclass.layers:
                                    layer_data = layer.query(
                                        geometry=True, variants=[_id]
                                    )
                                    for feature_sets in layer_data.resolve():
                                        if feature_sets["count"] > 0:
                                            logger.info(
                                                "Creating layer {}".format(layer.name)
                                            )
                                            self.json_to_file(  # type: ignore
                                                feature_sets["features"],
                                                subdir,
                                                layer.name,
                                                indent,
                                            )
                    pbar.update(1)

            if self.cli_mode:
                print("Export successfully finished.")

        else:
            logger.info("No VARIANTMASTER found. There should be no variants.")
            logger.info("Starting to export data in %s", output_directory)

            for objectclass in objectclasses:
                logger.debug("Exporting objectclass %s", objectclass)
                for layer in objectclass.layers:
                    logger.debug("Exporting layer %s", layer)
                    layer_data = layer.query(returnGeometry=True)
                    for layers in layer_data.resolve():
                        if layers["count"]:
                            self.json_to_file(  # type: ignore
                                layers,
                                os.path.join(output_directory, objectclass.name),
                                "_".join([layer.name, "Layers"]),
                                indent,
                            )
        logger.info("Export completed")
