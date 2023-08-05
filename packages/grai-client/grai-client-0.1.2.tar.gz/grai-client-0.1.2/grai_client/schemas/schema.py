from pathlib import Path
from typing import Any, Dict, Iterable, Type, Union

import yaml
from grai_client.schemas.edge import Edge, EdgeType
from grai_client.schemas.node import Node, NodeType
from grai_client.schemas.utilities import DispatchType
from multimethod import multimethod
from pydantic import BaseModel, Field
from typing_extensions import Annotated

GraiType = Union[Node, Edge]


class Schema(BaseModel):
    entity: Annotated[Union[Node, Edge], Field(discriminator="type")]

    @classmethod
    def to_model(cls, item: Dict, version: str, typing_type: Union[DispatchType, str]) -> GraiType:
        result = {
            "type": typing_type.type if isinstance(typing_type, DispatchType) else typing_type,
            "version": version,
            "spec": item,
        }
        return cls(entity=result).entity


def validate_file(file: Union[str, Path]) -> Iterable[GraiType]:
    with open(file) as f:
        for item in yaml.safe_load_all(f):
            yield Schema(entity=item).entity
