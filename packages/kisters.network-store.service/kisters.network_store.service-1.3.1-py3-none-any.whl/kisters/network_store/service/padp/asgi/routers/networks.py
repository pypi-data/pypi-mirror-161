import asyncio
import enum
from datetime import datetime
from typing import List, Optional, Union

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import ORJSONResponse
from kisters.network_store.model_library.base import (
    BaseElement,
    BaseGroup,
    BaseLink,
    Location,
    LocationExtent,
    LocationSet,
)
from kisters.network_store.model_library.util import all_groups, all_links, all_nodes
from pydantic import Field
from starlette import status

from kisters.network_store.service.sadp.mongodb import NetworkStore

_unique_link_class_names = sorted({e.__name__ for e in all_links})
_unique_node_class_names = sorted({e.__name__ for e in all_nodes})
_unique_group_class_names = sorted({e.__name__ for e in all_groups})

LinkClasses = enum.Enum(
    "LinkClasses", [(n.upper(), n) for n in _unique_link_class_names], type=str
)
NodeClasses = enum.Enum(
    "NodeClasses", [(n.upper(), n) for n in _unique_node_class_names], type=str
)
GroupClasses = enum.Enum(
    "GroupClasses", [(n.upper(), n) for n in _unique_group_class_names], type=str
)


class TopoNode(BaseElement):
    location: Optional[Location] = Field(None, description="Geographical location")
    schematic_location: Optional[Location] = Field(
        None, description="Schematic location"
    )


class TopoLink(BaseLink):
    pass


class TopoGroup(BaseGroup):
    pass


def get_networks_router(network_store: NetworkStore):
    networks = APIRouter()

    @networks.get("", response_model=List[str])
    async def list_existing_networks():
        return await network_store.get_networks()

    @networks.post("/{network_uid}")
    async def create_network(
        network_uid: str,
        links: Optional[List[Union[tuple(all_links)]]] = Body(None),
        nodes: Optional[List[Union[tuple(all_nodes)]]] = Body(None),
        groups: Optional[List[Union[tuple(all_groups)]]] = Body(None),
        delete_existing: bool = Query(
            True, description="Mark any existing elements as deleted"
        ),
        purge: bool = Query(
            False,
            description="If delete_existing, permanently delete "
            "elements (history is lost)",
        ),
    ):
        dt = network_store.make_datetime()
        if delete_existing:
            await asyncio.gather(
                network_store.drop_links(network_uid, dt=dt, purge=purge),
                network_store.drop_nodes(network_uid, dt=dt, purge=purge),
                network_store.drop_groups(network_uid, dt=dt, purge=purge),
            )
        if links:
            try:
                await network_store.save_links(
                    network_uid, [e.dict(exclude_none=True) for e in links], dt=dt
                )
            except ValueError as e:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
        if nodes:
            try:
                await network_store.save_nodes(
                    network_uid, [e.dict(exclude_none=True) for e in nodes], dt=dt
                )
            except ValueError as e:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
        if groups:
            try:
                await network_store.save_groups(
                    network_uid, [e.dict(exclude_none=True) for e in groups], dt=dt
                )
            except ValueError as e:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    @networks.delete("/{network_uid}")
    async def delete_all_network_elements(
        network_uid: str,
        purge: bool = Query(
            False, description="Permanently delete elements (history is lost)"
        ),
    ):
        if purge:
            await network_store.drop_network(network_uid)
        else:
            dt = network_store.make_datetime()
            await asyncio.gather(
                network_store.drop_links(network_uid, dt=dt),
                network_store.drop_nodes(network_uid, dt=dt),
                network_store.drop_groups(network_uid, dt=dt),
            )

    @networks.get("/{network_uid}/extent", response_model=LocationExtent)
    async def get_location_extent(
        network_uid: str,
        dt: Optional[datetime] = Query(None, alias="datetime"),
        location_set: LocationSet = Query(LocationSet.GEOGRAPHIC),
    ):
        return await network_store.get_extent(network_uid, location_set, dt=dt)

    @networks.post(
        "/{network_uid}/links/search",
        response_model=List[Union[(*all_links, TopoLink)]],
    )
    async def get_links(
        network_uid: str,
        uids: Optional[List[str]] = Body(None),
        display_names: Optional[List[str]] = Body(None),
        element_class: Optional[LinkClasses] = Query(None),
        group_uids: Optional[List[str]] = Body(None),
        include_subgroups: bool = Query(
            False,
            description="Recursively include groups that are subgroups of group_uids",
        ),
        datetime: Optional[datetime] = Query(
            None,
            description="Matches elements created and not deleted by this datetime",
        ),
        skip: int = Query(None),
        start_uid: Optional[str] = Query(
            None,
            description="Exclude elements with UIDs lexicographically less"
            " than this UID (much faster than skip)",
        ),
        start_uid_chunks: Optional[bool] = Query(
            None,
            description="Get only uids necessary for start_uid parameter."
            " Combine with `limit` to adjust chunk size. (Defaults to 1000)",
        ),
        limit: Optional[int] = Query(None),
        only_topology: Optional[bool] = Query(None),
        location_set: Optional[LocationSet] = Query(LocationSet.GEOGRAPHIC),
        adjacent_nodes: Optional[List[str]] = Body(None, alias="adjacent_node_uids"),
        only_interior: bool = Query(
            True,
            description="If adjacent nodes are provided, links must have"
            " both source and target nodes in adjacent_node",
        ),
    ):
        elements = await network_store.get_links(
            network_uid,
            uids=uids,
            display_names=display_names,
            element_class=element_class,
            group_uids=group_uids,
            include_subgroups=include_subgroups,
            dt=datetime,
            skip=skip,
            start_uid=start_uid,
            start_uid_chunks=start_uid_chunks,
            limit=limit,
            only_topology=only_topology,
            location_set=location_set,
            adjacent_nodes=adjacent_nodes,
            only_interior=only_interior,
        )
        return ORJSONResponse(content=elements)

    @networks.post(
        "/{network_uid}/nodes/search",
        response_model=List[Union[(*all_nodes, TopoNode)]],
    )
    async def get_nodes(
        network_uid: str,
        uids: Optional[List[str]] = Body(None),
        display_names: Optional[List[str]] = Body(None),
        element_class: Optional[NodeClasses] = Query(None),
        group_uids: Optional[List[str]] = Body(None),
        include_subgroups: bool = Query(
            False,
            description="Recursively include groups that are subgroups of group_uids",
        ),
        datetime: Optional[datetime] = Query(
            None,
            description="Matches elements created and not deleted by this datetime",
        ),
        skip: Optional[int] = Query(None),
        start_uid: Optional[str] = Query(
            None,
            description="Exclude elements with UIDs lexicographically less"
            " than this UID (much faster than skip)",
        ),
        start_uid_chunks: Optional[bool] = Query(
            None,
            description="Get only uids necessary for start_uid parameter."
            " Combine with `limit` to adjust chunk size. (Defaults to 1000)",
        ),
        limit: Optional[int] = Query(None),
        only_topology: Optional[bool] = Query(None),
        location_set: Optional[LocationSet] = Query(LocationSet.GEOGRAPHIC),
        extent: Optional[LocationExtent] = None,
        schematic_extent: Optional[LocationExtent] = None,
    ):
        elements = await network_store.get_nodes(
            network_uid,
            uids=uids,
            display_names=display_names,
            element_class=element_class,
            group_uids=group_uids,
            include_subgroups=include_subgroups,
            dt=datetime,
            skip=skip,
            start_uid=start_uid,
            start_uid_chunks=start_uid_chunks,
            limit=limit,
            only_topology=only_topology,
            location_set=location_set,
            extent=extent.dict(exclude_none=True) if extent else None,
            schematic_extent=schematic_extent.dict(exclude_none=True)
            if schematic_extent
            else None,
        )
        return ORJSONResponse(content=elements)

    @networks.post(
        "/{network_uid}/groups/search",
        response_model=List[Union[(*all_groups, TopoGroup)]],
    )
    async def get_groups(
        network_uid: str,
        uids: Optional[List[str]] = Body(None),
        group_uids: Optional[List[str]] = Body(None),
        include_subgroups: bool = Query(
            False,
            description="Recursively include groups that are subgroups of group_uids",
        ),
        display_names: Optional[List[str]] = Body(None),
        element_class: Optional[GroupClasses] = Query(None),
        datetime: Optional[datetime] = Query(
            None,
            description="Matches elements created and not deleted by this datetime",
        ),
        skip: Optional[int] = Query(None),
        start_uid: Optional[str] = Query(
            None,
            description="Exclude elements with UIDs lexicographically less"
            " than this UID (much faster than skip)",
        ),
        start_uid_chunks: Optional[bool] = Query(
            None,
            description="Get only uids necessary for start_uid parameter."
            " Combine with `limit` to adjust chunk size. (Defaults to 1000)",
        ),
        limit: Optional[int] = Query(None),
    ):
        elements = await network_store.get_groups(
            network_uid,
            uids=uids,
            group_uids=group_uids,
            include_subgroups=include_subgroups,
            display_names=display_names,
            element_class=element_class,
            dt=datetime,
            skip=skip,
            start_uid=start_uid,
            start_uid_chunks=start_uid_chunks,
            limit=limit,
        )
        return ORJSONResponse(content=elements)

    @networks.post("/{network_uid}/links")
    async def new_links(
        network_uid: str,
        elements: List[Union[tuple(all_links)]] = Body(..., embed=True),
        datetime: Optional[datetime] = Query(
            None, description="The timestamp that will be used for the request"
        ),
    ):
        try:
            await network_store.save_links(
                network_uid, [e.dict(exclude_none=True) for e in elements], dt=datetime
            )
        except ValueError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    @networks.post("/{network_uid}/nodes")
    async def new_nodes(
        network_uid: str,
        elements: List[Union[tuple(all_nodes)]] = Body(..., embed=True),
        datetime: Optional[datetime] = Query(
            None, description="The timestamp that will be used for the request"
        ),
    ):
        try:
            await network_store.save_nodes(
                network_uid, [e.dict(exclude_none=True) for e in elements], dt=datetime
            )
        except ValueError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    @networks.post("/{network_uid}/groups")
    async def new_groups(
        network_uid: str,
        elements: List[Union[tuple(all_groups)]] = Body(..., embed=True),
        datetime: Optional[datetime] = Query(
            None, description="The timestamp that will be used for the request"
        ),
    ):
        try:
            await network_store.save_groups(
                network_uid, [e.dict(exclude_none=True) for e in elements], dt=datetime
            )
        except ValueError as e:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    @networks.delete("/{network_uid}/links")
    async def delete_links(
        network_uid: str,
        uid: Optional[List[str]] = Query(
            None, description="Limit deletion to a set of `uid`s"
        ),
        uids: Optional[List[str]] = Body(
            None,
            description="Limit deletion to a set of `uid`s",
            embed=True,
            deprecated=True,
        ),
        group_uid: Optional[List[str]] = Query(
            None, description="Limit deletion to a set of `group_uid`s"
        ),
        group_uids: Optional[List[str]] = Body(
            None,
            description="Limit deletion to a set of `group_uid`s",
            embed=True,
            deprecated=True,
        ),
        purge: bool = Query(
            False, description="Permanently delete elements (history is lost)"
        ),
        datetime: Optional[datetime] = Query(
            None,
            description="The timestamp that will be used for the request",
        ),
    ):
        if uid:
            if uids:
                uids.extend(uid)
            else:
                uids = uid
        if group_uid:
            if group_uids:
                group_uids.extend(group_uid)
            else:
                group_uids = group_uid
        await network_store.drop_links(
            network_uid, uids=uids, group_uids=group_uids, purge=purge, dt=datetime
        )

    @networks.delete("/{network_uid}/nodes")
    async def delete_nodes(
        network_uid: str,
        uid: Optional[List[str]] = Query(
            None, description="Limit deletion to a set of `uid`s"
        ),
        uids: Optional[List[str]] = Body(
            None,
            description="Limit deletion to a set of `uid`s",
            embed=True,
            deprecated=True,
        ),
        group_uid: Optional[List[str]] = Query(
            None, description="Limit deletion to a set of `group_uid`s"
        ),
        group_uids: Optional[List[str]] = Body(
            None,
            description="Limit deletion to a set of `group_uid`s",
            embed=True,
            deprecated=True,
        ),
        purge: bool = Query(
            False, description="Permanently delete elements (history is lost)"
        ),
        datetime: Optional[datetime] = Query(
            None, description="The timestamp that will be used for the request"
        ),
    ):
        if uid:
            if uids:
                uids.extend(uid)
            else:
                uids = uid
        if group_uid:
            if group_uids:
                group_uids.extend(group_uid)
            else:
                group_uids = group_uid
        await network_store.drop_nodes(
            network_uid, uids=uids, group_uids=group_uids, purge=purge
        )

    @networks.delete("/{network_uid}/groups")
    async def delete_groups(
        network_uid: str,
        uid: Optional[List[str]] = Query(
            None, description="Limit deletion to a set of `uid`s"
        ),
        uids: Optional[List[str]] = Body(
            None,
            description="Limit deletion to a set of `uid`s",
            embed=True,
            deprecated=True,
        ),
        group_uid: Optional[List[str]] = Query(
            None, description="Limit deletion to a set of `group_uid`s"
        ),
        group_uids: Optional[List[str]] = Body(
            None,
            description="Limit deletion to a set of `group_uid`s",
            embed=True,
            deprecated=True,
        ),
        purge: bool = Query(
            False, description="Permanently delete elements (history is lost)"
        ),
        datetime: Optional[datetime] = Query(
            None, description="The timestamp that will be used for the request"
        ),
    ):
        if uid:
            if uids:
                uids.extend(uid)
            else:
                uids = uid
        if group_uid:
            if group_uids:
                group_uids.extend(group_uid)
            else:
                group_uids = group_uid
        await network_store.drop_groups(
            network_uid, uids=uids, group_uids=group_uids, purge=purge, dt=datetime
        )

    return networks
