from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from encord.objects.common import (
    Attribute,
    Shape,
    attribute_from_dict,
    attributes_to_list_dict,
)


@dataclass
class Object:
    """
    This class is currently in BETA. Its API might change in future minor version releases.
    """

    uid: int
    name: str
    color: str
    shape: Shape
    feature_node_hash: str
    attributes: List[Attribute] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> Object:
        shape_opt = Shape.from_string(d["shape"])
        if shape_opt is None:
            raise TypeError(f"The shape '{d['shape']}' of the object '{d}' is not recognised")

        attributes_ret: List[Attribute] = list()
        if "attributes" in d:
            for attribute_dict in d["attributes"]:
                attributes_ret.append(attribute_from_dict(attribute_dict))

        object_ret = Object(
            uid=int(d["id"]),
            name=d["name"],
            color=d["color"],
            shape=shape_opt,
            feature_node_hash=d["featureNodeHash"],
            attributes=attributes_ret,
        )

        return object_ret

    def to_dict(self) -> dict:
        ret = dict()
        ret["id"] = str(self.uid)
        ret["name"] = self.name
        ret["color"] = self.color
        ret["shape"] = self.shape.value
        ret["featureNodeHash"] = self.feature_node_hash

        attributes_list = attributes_to_list_dict(self.attributes)
        if attributes_list:
            ret["attributes"] = attributes_list

        return ret
