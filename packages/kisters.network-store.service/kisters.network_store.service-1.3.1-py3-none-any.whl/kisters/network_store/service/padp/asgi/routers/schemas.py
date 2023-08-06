import enum

from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from kisters.network_store.model_library.util import elements_mapping
from starlette import status


class Collection(str, enum.Enum):
    LINKS = "links"
    NODES = "nodes"
    GROUPS = "groups"


def get_schemas_router():
    schemas = APIRouter()

    @schemas.get("/{domain}/{collection}/{class_name}", response_class=ORJSONResponse)
    async def get_schema(domain: str, collection: Collection, class_name: str):
        try:
            element_class = elements_mapping[domain][collection][class_name]
        except KeyError:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return element_class.schema()

    return schemas
