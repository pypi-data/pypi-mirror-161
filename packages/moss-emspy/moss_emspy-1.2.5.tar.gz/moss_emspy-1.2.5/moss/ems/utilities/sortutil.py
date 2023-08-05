#
# Copyright (c) 2020  by M.O.S.S. Computer Grafik Systeme GmbH
#                         Hohenbrunner Weg 13
#                         D-82024 Taufkirchen
#                         http://www.moss.de#


class ObjectClassSorter:
    """
    Hierarchical ObjectClassSorter

    Examples:
        Builds an objectclass sorter

        >>> sorter = ObjectClassSorter(objectclasses)
        >>> result = sorter.by_reference()
    """

    def __init__(self, objectclasses):
        """
        Creates a new ObjectClassSorter instance.

        Args:
            objectclasses: The list of ObjectClasses to sort
        """
        self.objectclasses = objectclasses

    def by_reference(self):
        """
        Sorts the ObjectClasses by reference.
        """

        collected = []

        for root in self._get_root():
            collected.extend(self._collect(root))

        return collected

    def _collect(self, objectclass):
        collected = []

        collected.append(objectclass)

        for child in self._get_children(objectclass):
            collected.extend(self._collect(child))

        return collected

    def _get_children(self, objectclass):
        objectclasses = filter(
            lambda oc: objectclass != oc
            and self._is_referencing(oc.fields, objectclass),
            self.objectclasses,
        )

        return list(objectclasses)

    def _is_referencing(self, fields, objectclass):
        fields = filter(self._is_objectclass_field, fields)
        return any(field["objectClassName"] == objectclass.name for field in fields)

    def _get_root(self):
        return list(filter(lambda oc: not self._has_references(oc), self.objectclasses))

    def _has_references(self, objectclass):
        return any(
            self._is_objectclass_field(field)
            and field["objectClassName"] != objectclass.name
            for field in objectclass.fields
        )

    def _is_objectclass_field(self, field):
        return field["type"] == "emsFieldTypeObjectClass"
