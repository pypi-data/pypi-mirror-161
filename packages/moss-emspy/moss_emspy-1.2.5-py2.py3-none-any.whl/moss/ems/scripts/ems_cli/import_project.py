import json
import os

from anytree import PreOrderIter, RenderTree
from anytree.importer import JsonImporter

from moss.ems import emsservice


def get_master_id(layer):

    features = list(layer.query(where="1=1").resolve())[0]["features"]
    sorted_features = sorted(
        features, key=lambda feature: feature["attributes"]["ID"], reverse=True
    )
    return sorted_features[0]["attributes"]["ID"]


def import_project():
    """
    Import data in a Project
    """

    BASE_PATH = "C:/temp/export_ems/"
    FILE_PATH = os.path.join(BASE_PATH, "variants_tree.json")

    PROJECT_FILE = os.path.join(BASE_PATH, "project.json")

    service = emsservice.Service(
        "http://localhost:32800/wega-ems/", "Erfassung", "Erfassung"
    )
    KEY_REMOVE = ["GLOBALID"]

    service.delete_project("random1")

    with open(PROJECT_FILE, "r+", encoding="utf-8") as old_project:
        service.import_project(json.load(old_project), "random1")

    importer = JsonImporter()
    with open(FILE_PATH, "r", encoding="utf-8") as variants_tree:
        root = importer.read(variants_tree)
        print(RenderTree(root))
        iterable_tree = PreOrderIter(root)
        for node in iterable_tree:
            if node.name != "0":
                # Node is master
                if node.master:
                    # Add master from fileystem
                    master_path = os.path.join(BASE_PATH, node.name, "master.json")
                    with open(master_path, "r", encoding="utf-8") as master_feature:
                        master_feature_json = json.load(master_feature)
                        for key in KEY_REMOVE:
                            master_feature_json["attributes"].pop(key)

                        project = service.project("random1")
                        objectclass = project.objectclass("WP")
                        layer = objectclass.layers[0]
                        layer.add_features([master_feature_json])
                        current_master_id = get_master_id(layer)
                        node.new_id = current_master_id
                        derive_response = objectclass.derive(
                            current_master_id, current_master_id, "pippo", "nutria"
                        )

                        print(derive_response)

        # current_master_id = None
        # current_parent_id = None
        # for node in iterable_tree:
        #     if node.name != "0":
        #         # Node is master
        #         if node.master:
        #             # Add master from fileystem
        #             master_path = os.path.join(BASE_PATH, node.name, "master.json")
        #             with open(master_path, "r", encoding="utf-8") as master_feature:
        #                 master_feature_json = json.load(master_feature)
        #                 for key in KEY_REMOVE:
        #                     master_feature_json["attributes"].pop(key)

        #                 project = service.project("random1")
        #                 objectclass = project.objectclass("WP")
        #                 layer = objectclass.layers[0]
        #                 layer.add_features([master_feature_json])
        #                 current_master_id = get_master_id(layer)
        #                 node.new_id = current_master_id
        # derive_response = objectclass.derive(
        #     current_master_id, current_master_id, "pippo", "nutria"
        # )

        # current_parent_id = derive_response["deriveVariantResult"][
        #     "objectId"
        # ]

        # Get the id of the new master

        # else:
        #     project = service.project("random1")
        #     objectclass = project.objectclass("WP")
        #     derive_response = objectclass.derive(
        #         current_master_id, current_parent_id, "pippo", "nutria"
        #     )
        #     current_parent_id = derive_response["deriveVariantResult"][
        #         "objectId"
        #     ]

    # print(root)
    # iterable_tree = PreOrderIter(root)
    # for i in iterable_tree:
    #    print(i)

    # variants_mapping = {}
    # master_mapping = {}

    # for node in iterable_tree:
    #     current_master_id = None
    #     current_parent_id = None
    #     # Add this node
    #     if node.master:
    #         # Add master from fileystem
    #         master_path = os.path.join(BASE_PATH, node.name, "master.json")
    #         with open(master_path, "r", encoding="utf-8") as master_feature:
    #             master_feature_json = json.load(master_feature)
    #             master_feature_id = master_feature_json["attributes"]["ID"]

    #             if master_feature_id not in master_mapping.keys():
    #                 for key in KEY_REMOVE:
    #                     master_feature_json["attributes"].pop(key)

    #                 project = service.project("random1")
    #                 objectclass = project.objectclass("WP")
    #                 layer = objectclass.layers[0]
    #                 layer.add_features([master_feature_json])
    #                 current_master_id = get_master_id(layer)
    #                 # Add to mapping
    #                 master_mapping[master_feature_id] = current_master_id

    #     # Derive the children
    #     name = node.name
    #     for child_node in findall_by_attr(node, name, "parent_id"):


if __name__ == "__main__":
    import_project()
