from __future__ import annotations

from typing import List, Union

from XmlElement import XmlElement

from .const import FieldGroupOperators
from .query_condition_field import QueryConditionField


class QueryConditionGroup:
    def __init__(
        self,
        object_name: str,
        field_conditions: Union[QueryConditionField, List[QueryConditionField]],
        group_operator: FieldGroupOperators = FieldGroupOperators.AND,
        field_groups: Union[QueryConditionGroup, List[QueryConditionGroup]] = None,
    ):
        """Create a new QueryConditionGroup() object combining the `<ConditionObject>` and `<FieldGroup>` tags.

        TODO
        Keyword arguments:
        object_name -- The internal name of a folder, register or document type.
        field_conditions -- A list of or single QueryConditionField(s).
        field_groups -- (Optional) A list of or single QueryConditionGroup(s).
        group_operator -- (Optional) FieldGroupOperators, default = FieldGroupOperators.AND.
        """
        self.internal_name = object_name
        if isinstance(field_conditions, list):
            self.field_conditions = field_conditions
        else:
            self.field_conditions = [field_conditions]

        if field_groups is None:
            self.field_groups = []
        elif isinstance(field_groups, list):
            self.field_groups = field_groups
        else:
            self.field_groups = [field_groups]

        for field_group in self.field_groups:
            assert (
                field_group.internal_name == self.internal_name
            ), f"The object_name of a sub field_group must match the object_name parent field_group. parent: {self.internal_name} != sub: {field_group.internal_name}"

        self.group_operator = group_operator

    def __repr__(self) -> str:
        return f"{self.internal_name} ({self.group_operator.value}): {self.field_conditions}"

    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement"""
        return XmlElement(
            "FieldGroup",
            {"operator": self.group_operator.value},
            [x.to_xml_element() for x in self.field_conditions] + [x.to_xml_element() for x in self.field_groups],
        )
