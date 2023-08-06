from typing import Union

from XmlElement import XmlElement

from .const import SortOrder, SystemFields


class QueryResultField:
    def __init__(
        self,
        field: Union[str, SystemFields],
        sort_pos: Union[int, None] = None,
        sort_order: Union[SortOrder, None] = None,
    ):
        """Create a new QueryResultField() object.

        Keyword arguments:
        field -- A internal name as string or a instance of SystemFields. Internal names beeing automatically checked against known system field names.
        sort_pos -- (Optional) int of the sort position in a query, default = None.
        sort_order -- (Optional) SortOrder instance for this field, default = SortOrder.NONE if sort_pos = None else SortOrder.ASC
        """

        if isinstance(field, SystemFields):
            self.internal_name = field.name
            self.system = True
        elif field in [system_field.name for system_field in SystemFields]:
            self.internal_name = field
            self.system = True
        else:
            self.internal_name = field
            self.system = False

        self.sort_pos = sort_pos

        if sort_order is None and sort_pos is not None:
            self.sort_order = SortOrder.ASC
        else:
            self.sort_order = sort_order if sort_order else SortOrder.NONE

    def __repr__(self) -> str:
        return f"{self.internal_name} (system:{1 if self.system else 0}, sort_pos:{self.sort_pos}, sort_order:{self.sort_order.name})"

    def to_xml_element(self) -> XmlElement:
        """Render self to XmlElement"""
        xml = XmlElement("Field", {"internal_name": self.internal_name})
        if self.system:
            xml.attributes["system"] = "1"

        if self.sort_pos and self.sort_pos > 0 and self.sort_order != SortOrder.NONE:
            xml.attributes["sortpos"] = str(self.sort_pos)
            xml.attributes["sortorder"] = self.sort_order.name

        return xml
