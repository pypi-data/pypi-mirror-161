import logging

logger = logging.getLogger("ems_cli_compare")


class EmsCliCompare:
    def ems_compare(self, project_name1, project_name2):
        # type: (str, str) -> None
        """Compares two EMS projects

        Args:
            project_name1: the name of the first EMS project
            project_name2: the name of the second EMS project

        Returns:

        Raises:
            EmsCliException
        """
        from moss.ems.scripts.ems_cli import EmsCliException

        logger.info(
            "Start comparing project '{}' with project '{}'".format(
                project_name1, project_name2
            )
        )
        logger.debug(
            "Projects in the current instance: %s",
            self.ems_service.projects,  # type: ignore
        )
        error_counter = 0
        error_log = []

        project1 = next(
            iter(filter(lambda p: p.name == project_name1, self.ems_service.projects)),  # type: ignore
            None,
        )

        if project1 is None:
            logger.error(
                "The first project '%s' does not exist in this instance", project_name1
            )
            raise EmsCliException(
                "The first project '{}' does not exist in this instance".format(
                    project_name1
                )
            )

        project2 = next(
            iter(filter(lambda p: p.name == project_name2, self.ems_service.projects)),  # type: ignore
            None,
        )

        if project2 is None:
            logger.error(
                "The second project '%s' does not exist in this instance", project_name2
            )
            raise EmsCliException(
                "The second project '{}' does not exist in this instance".format(
                    project_name2
                )
            )

        # Check if the project has variant
        objectclasses1 = project1.objectclasses
        # Looking for the VNT Master Objectclass
        variant_master_found1 = None
        variant_master_found1 = next(
            (item for item in objectclasses1 if item.objectClassType == "VNTMASTER"), None  # type: ignore
        )
        # Check if the project has variant
        objectclasses2 = project2.objectclasses
        # Looking for the VNT Master Objectclass
        variant_master_found2 = None
        variant_master_found2 = next(
            (item for item in objectclasses2 if item.objectClassType == "VNTMASTER"), None  # type: ignore
        )
        logger.info("Starting Compare")
        if variant_master_found1:
            logger.info(
                "An objectclass of type 'VNTMASTER' was found in {}. Switching to"
                " variant mode!".format(project1)
            )
            if variant_master_found2:
                logger.info(
                    "An objectclass of type 'VNTMASTER' was also found in {}.".format(
                        project2
                    )
                )

            query_results1 = variant_master_found1.layers[0].query()
            query_results2 = variant_master_found2.layers[0].query()

            featureid_name1 = list(query_results1.resolve())[0]["objectIdFieldName"]
            featureid_name2 = list(query_results2.resolve())[0]["objectIdFieldName"]
            for query1 in list(query_results1.resolve())[0]["features"]:
                # since an error count greater than 100 continuation makes no sense
                if error_counter >= 100:
                    break
                featureid1 = query1["attributes"][featureid_name1]
                if (
                    len(
                        [
                            q
                            for q in list(query_results2.resolve())[0]["features"]
                            if q["attributes"]["GUID"] == query1["attributes"]["GUID"]
                        ]
                    )
                    > 1
                ):
                    logger.error(
                        "GUID {} is not unique".format(query1["attributes"]["GUID"])
                    )
                query2 = next(
                    (
                        q
                        for q in list(query_results2.resolve())[0]["features"]
                        if q["attributes"]["GUID"] == query1["attributes"]["GUID"]
                    ),
                    None,
                )
                featureid2 = query2["attributes"][featureid_name2]
                logger.info(
                    "Comparing master feature {}, comparing with {}".format(
                        featureid1, featureid2
                    )
                )
                variants1 = variant_master_found1.variants(featureid1)
                variants2 = variant_master_found2.variants(featureid2)
                for variant1 in variants1:
                    if error_counter >= 100:
                        break
                    _id1 = variant1[featureid_name1]
                    if len([v for v in variants2 if v["NAME"] == variant1["NAME"]]) > 1:
                        logger.error(
                            "Variant name {} is not unique".format(variant1["NAME"])
                        )
                    variant2 = next(
                        (v for v in variants2 if v["NAME"] == variant1["NAME"]), None
                    )
                    _id2 = variant2[featureid_name2]
                    logger.info(
                        "Comparing variant {} comparing with {}".format(_id1, _id2)
                    )
                    for objectclass in objectclasses1:
                        if error_counter >= 100:
                            break
                        if objectclass.has_variant:
                            logger.info(
                                "Comparing objectclass {}".format(objectclass.name)
                            )
                            for layer in objectclass.layers:
                                logger.info(
                                    "Comparing layer data for layer {}".format(
                                        layer.name
                                    )
                                )
                                layer_data1 = layer.query(variants=[_id1])
                                layer_data2 = (
                                    project2.objectclass(objectclass.name)
                                    .layer(layer.name)
                                    .query(variants=[_id2])
                                )
                                # features1 = list(layer_data1.resolve())
                                # features2 = list(layer_data2.resolve())
                                if layer_data1.length != layer_data2.length:
                                    error_message = (
                                        "Feature list count of {}/{}/{}/{} is NOT equal"
                                        " ({} != {})!".format(
                                            project1,
                                            variant1["NAME"],
                                            objectclass.name,
                                            layer.name,
                                            layer_data1.length,
                                            layer_data2.length,
                                        )
                                    )
                                    logger.error(error_message)
                                    error_log.append(error_message)
                                    error_counter += 1
                                    if error_counter >= 100:
                                        logger.error(
                                            "Too many differences: stopping the"
                                            " compare."
                                        )
                                        break

        else:
            logger.info("No VARIANTMASTER found.")

            for objectclass in objectclasses1:
                logger.debug("Comparing objectclass %s", objectclass)
                for layer in objectclass.layers:
                    logger.debug("Comparing layer data for layer %s", layer)
                    layer_data1 = layer.query()
                    layer_data2 = (
                        project2.objectclass(objectclass.name).layer(layer.name).query()
                    )
                    if layer_data1.length != layer_data2.length:
                        error_message = (
                            "Feature list count of {}/{}/{} is NOT equal ({} != {})!"
                            .format(
                                project1,
                                objectclass.name,
                                layer.name,
                                layer_data1.length,
                                layer_data2.length,
                            )
                        )
                        logger.error(error_message)
                        error_log.append(error_message)
                        error_counter += 1
                        if error_counter >= 100:
                            logger.error("Too many differences: stopping the compare.")
                            break
        if error_counter > 0:
            logger.info(
                "Compare completed with {} errors!\nError log summary:\n".format(
                    error_counter
                )
            )
            logger.error("\n".join(map(str, error_log)))
        else:
            logger.info("Compare completed successfully.")
