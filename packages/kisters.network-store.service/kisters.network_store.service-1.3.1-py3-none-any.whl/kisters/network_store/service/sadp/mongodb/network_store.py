import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple, Union

import pymongo
from kisters.network_store.model_library.base import LocationSet

from .settings import MongoDBMotorClientEnvironmentVariables

logger = logging.getLogger(__name__)


link_loc_attr_map = {
    LocationSet.SCHEMATIC: "schematic_vertices",
    LocationSet.GEOGRAPHIC: "vertices",
}


class NetworkStore:
    def __init__(self, *, event_loop=None, **kwargs):
        connection = MongoDBMotorClientEnvironmentVariables(**kwargs)
        self._client = connection.create_client(io_loop=event_loop)
        self._network_database_prefix = connection.network_database_prefix
        self._initialized_networks: Set[str] = set()

    @classmethod
    def make_datetime(cls, dt: Optional[Union[datetime, str]] = None) -> datetime:
        if not dt:
            dt = datetime.now(timezone.utc)
        elif isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.astimezone(timezone.utc).replace(
            # mongodb precision
            microsecond=(dt.microsecond - dt.microsecond % 1000)
        )

    async def get_networks(self) -> List[str]:
        names = await self._client.list_database_names()
        idx = len(self._network_database_prefix)
        return [n[idx:] for n in names if n.startswith(self._network_database_prefix)]

    async def get_links(
        self,
        network: str,
        *,
        only_topology: bool = False,
        location_set: Optional[LocationSet] = LocationSet.GEOGRAPHIC,
        uids: Optional[List[str]] = None,
        display_names: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        include_subgroups: bool = False,
        element_class: Optional[str] = None,
        dt: Optional[datetime] = None,
        skip: Optional[int] = None,
        start_uid: Optional[str] = None,
        start_uid_chunks: Optional[bool] = None,
        limit: Optional[int] = None,
        adjacent_nodes: Optional[List[str]] = None,
        only_interior: bool = True,
    ) -> List[Dict]:
        if adjacent_nodes:
            extra_query_filter = {
                "$and"
                if only_interior
                else "$or": [
                    {"source_uid": {"$in": adjacent_nodes}},
                    {"target_uid": {"$in": adjacent_nodes}},
                ]
            }
        else:
            extra_query_filter = None

        if only_topology:
            extra_projection = {
                "domain": True,
                "element_class": True,
                "uid": True,
                "source_uid": True,
                "target_uid": True,
                "group_uid": True,
            }
            extra_projection[link_loc_attr_map[location_set]] = True
        else:
            extra_projection = None

        return await self._get_elements(
            network,
            "links",
            uids=uids,
            display_names=display_names,
            element_class=element_class,
            group_uids=group_uids,
            include_subgroups=include_subgroups,
            dt=dt,
            skip=skip,
            start_uid=start_uid,
            start_uid_chunks=start_uid_chunks,
            limit=limit,
            extra_query_filter=extra_query_filter,
            extra_projection=extra_projection,
        )

    async def get_nodes(
        self,
        network: str,
        *,
        only_topology: bool = False,
        location_set: Optional[LocationSet] = LocationSet.GEOGRAPHIC,
        uids: Optional[List[str]] = None,
        display_names: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        include_subgroups: bool = False,
        element_class: Optional[str] = None,
        dt: Optional[datetime] = None,
        skip: Optional[int] = None,
        start_uid: Optional[str] = None,
        start_uid_chunks: Optional[bool] = None,
        limit: Optional[int] = None,
        extent: Optional[Dict[str, Tuple[float, float]]] = None,
        schematic_extent: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> List[Dict]:
        extra_query_filter = None
        if extent:
            extra_query_filter = extra_query_filter or {}
            for dimension, bounds in extent.items():
                extra_query_filter[f"location.{dimension}"] = {
                    "$gte": bounds[0],
                    "$lte": bounds[1],
                }
        if schematic_extent:
            extra_query_filter = extra_query_filter or {}
            for dimension, bounds in schematic_extent.items():
                extra_query_filter[f"schematic_location.{dimension}"] = {
                    "$gte": bounds[0],
                    "$lte": bounds[1],
                }

        if only_topology:
            extra_projection = {
                "domain": True,
                "element_class": True,
                "uid": True,
                "group_uid": True,
            }
            extra_projection[location_set] = True
        else:
            extra_projection = None

        return await self._get_elements(
            network,
            "nodes",
            uids=uids,
            display_names=display_names,
            element_class=element_class,
            group_uids=group_uids,
            include_subgroups=include_subgroups,
            dt=dt,
            skip=skip,
            start_uid=start_uid,
            start_uid_chunks=start_uid_chunks,
            limit=limit,
            extra_query_filter=extra_query_filter,
            extra_projection=extra_projection,
        )

    async def get_groups(
        self,
        network: str,
        *,
        uids: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        include_subgroups: bool = False,
        display_names: Optional[List[str]] = None,
        element_class: Optional[str] = None,
        dt: Optional[datetime] = None,
        skip: Optional[int] = None,
        start_uid: Optional[str] = None,
        start_uid_chunks: Optional[bool] = None,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        return await self._get_elements(
            network,
            "groups",
            uids=uids,
            group_uids=group_uids,
            include_subgroups=include_subgroups,
            display_names=display_names,
            element_class=element_class,
            dt=dt,
            skip=skip,
            start_uid=start_uid,
            start_uid_chunks=start_uid_chunks,
            limit=limit,
        )

    @classmethod
    def _add_created(cls, elements: List[dict], created: datetime):
        """Sets the 'created' field in elements if unset"""
        for e in elements:
            if e.get("created") is None:
                e["created"] = created

    async def save_nodes(
        self, network: str, elements: List[Dict], *, dt: Optional[datetime] = None
    ):
        await self._save_elements(network, elements, collection="nodes", dt=dt)

    async def save_links(
        self, network: str, elements: List[Dict], *, dt: Optional[datetime] = None
    ):
        await self._save_elements(network, elements, collection="links", dt=dt)

    async def drop_links(
        self,
        network: str,
        *,
        uids: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        purge: bool = False,
        dt: Optional[datetime] = None,
    ):
        await self._drop_elements(
            network,
            collection="links",
            uids=uids,
            group_uids=group_uids,
            purge=purge,
            dt=dt,
        )

    async def drop_nodes(
        self,
        network: str,
        *,
        uids: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        purge: bool = False,
        dt: Optional[datetime] = None,
    ):
        await self._drop_elements(
            network,
            collection="nodes",
            uids=uids,
            group_uids=group_uids,
            purge=purge,
            dt=dt,
        )

    async def save_groups(
        self, network: str, elements: List[Dict], *, dt: Optional[datetime] = None
    ):
        await self._save_elements(network, elements, collection="groups", dt=dt)

    async def drop_groups(
        self,
        network: str,
        *,
        uids: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        purge: bool = False,
        dt: Optional[datetime] = None,
    ):
        await self._drop_elements(
            network,
            collection="groups",
            uids=uids,
            group_uids=group_uids,
            purge=purge,
            dt=dt,
        )

    async def drop_network(self, network: str):
        self._initialized_networks.discard(network)
        logger.warning(f'Dropping network store database "{network}"')
        network = self._network_database_prefix + network
        await self._client.drop_database(network)

    async def get_extent(
        self, network: str, location_set: str, *, dt: Optional[datetime] = None
    ) -> Dict:
        query_filter = {}
        dt = self.make_datetime(dt)
        query_filter["created"] = {"$lte": dt}
        query_filter["$or"] = [
            {"deleted": {"$gt": dt}},
            {"deleted": {"$exists": False}},
        ]
        pipeline = []
        if query_filter:
            pipeline.append({"$match": query_filter})
        pipeline.append(
            {
                "$group": {
                    "_id": None,
                    **{
                        f"{dim}__{i}": {
                            "$max" if i else "$min": f"${location_set}.{dim}"
                        }
                        for dim in ("x", "y", "z")
                        for i in (0, 1)
                    },
                }
            }
        )

        collection = self._get_collection(network, "nodes")
        raw_extent = None
        async for doc in collection.aggregate(pipeline):
            raw_extent = doc
            del raw_extent["_id"]
        raw_extent = raw_extent or {}

        extent = {}
        for key, value in raw_extent.items():
            dim_name, idx = key.split("__")
            extent[dim_name] = extent.get(dim_name, [None, None])
            extent[dim_name][int(idx)] = value

        return extent

    async def _initialize_network(self, network: str) -> None:
        if network in self._initialized_networks:
            return

        db = self._client[self._network_database_prefix + network]

        await asyncio.gather(
            # UID indices
            db.nodes.create_index(
                [
                    ("uid", pymongo.ASCENDING),
                    ("created", pymongo.ASCENDING),
                    ("deleted", pymongo.ASCENDING),
                ]
            ),
            db.links.create_index(
                [
                    ("uid", pymongo.ASCENDING),
                    ("created", pymongo.ASCENDING),
                    ("deleted", pymongo.ASCENDING),
                ]
            ),
            db.groups.create_index(
                [
                    ("uid", pymongo.ASCENDING),
                    ("created", pymongo.ASCENDING),
                    ("deleted", pymongo.ASCENDING),
                ]
            ),
            # Group UID indices
            db.nodes.create_index(
                [
                    ("group_uid", pymongo.ASCENDING),
                    ("created", pymongo.ASCENDING),
                    ("deleted", pymongo.ASCENDING),
                ]
            ),
            db.links.create_index(
                [
                    ("group_uid", pymongo.ASCENDING),
                    ("created", pymongo.ASCENDING),
                    ("deleted", pymongo.ASCENDING),
                ]
            ),
            db.groups.create_index(
                [
                    ("group_uid", pymongo.ASCENDING),
                    ("created", pymongo.ASCENDING),
                    ("deleted", pymongo.ASCENDING),
                ]
            ),
        )

        self._initialized_networks.add(network)

    def _get_collection(self, network, collection):
        return self._client[self._network_database_prefix + network][collection]

    async def _get_elements(
        self,
        network: str,
        collection: str,
        *,
        uids: Optional[List[str]] = None,
        display_names: Optional[List[str]] = None,
        element_class: Optional[str] = None,
        group_uids: Optional[List[str]] = None,
        include_subgroups: bool = False,
        dt: Optional[datetime] = None,
        skip: Optional[int] = None,
        start_uid: Optional[str] = None,
        start_uid_chunks: Optional[bool] = None,
        limit: Optional[int] = None,
        extra_query_filter: Optional[Dict] = None,
        extra_projection: Optional[Dict] = None,
    ) -> List[Dict]:
        query_filter = extra_query_filter or {}
        projection = {"_id": False}
        if start_uid_chunks:
            projection["uid"] = True
        elif extra_projection:
            projection.update(extra_projection)
        dt = self.make_datetime(dt)
        query_filter["created"] = {"$lte": dt}
        query_filter["$or"] = [
            {"deleted": {"$gt": dt}},
            {"deleted": {"$exists": False}},
        ]
        if start_uid:
            query_filter["uid"] = {"$gte": start_uid}
        if uids is not None:
            query_filter["uid"] = {"$in": uids}
        if display_names is not None:
            query_filter["display_name"] = {"$in": display_names}
        if element_class is not None:
            query_filter["element_class"] = element_class
        if group_uids is not None:
            if include_subgroups:
                group_uids = await self._get_subgroups(network, group_uids, dt)
            query_filter["group_uid"] = {"$in": group_uids}
        collection = self._get_collection(network, collection)
        cursor = collection.find(filter=query_filter, projection=projection)
        if skip is not None or start_uid or limit is not None or start_uid_chunks:
            cursor.sort("uid", pymongo.ASCENDING)
        if skip is not None:
            cursor.skip(skip)
        if limit is not None and not start_uid_chunks:
            cursor.limit(limit)
        if start_uid_chunks:
            elements = []
            i = 0
            _l = limit or 1000
            async for e in cursor:
                if i % _l == 0:
                    elements.append(e["uid"])
                i += 1
        else:
            elements = await cursor.to_list(None)
        return elements

    async def _save_elements(
        self,
        network: str,
        elements: List[Dict],
        *,
        collection: str,
        dt: Optional[datetime] = None,
    ):
        self._check_for_duplicate_uids(elements)
        await self._initialize_network(network)
        dt = self.make_datetime(dt)
        await self._drop_elements(
            network, uids=[e["uid"] for e in elements], collection=collection, dt=dt
        )
        self._add_created(elements, dt)
        collection = self._get_collection(network, collection)
        await collection.insert_many(elements)

    async def _drop_elements(
        self,
        network: str,
        *,
        collection: str,
        uids: Optional[List[str]] = None,
        group_uids: Optional[List[str]] = None,
        purge: bool = False,
        dt: Optional[datetime] = None,
    ):
        query_filter = {}
        if uids is not None:
            query_filter["uid"] = {"$in": uids}
        if group_uids is not None:
            query_filter["group_uid"] = {"$in": group_uids}
        collection = self._get_collection(network, collection)
        if purge:
            logger.warning("Purging all %s from database '%s'", collection, network)
            await collection.delete_many(query_filter)
        else:
            logger.debug(
                "Marking as deleted %s from collection '%s': %s",
                collection,
                network,
                (uids if uids else "all"),
            )
            dt = self.make_datetime(dt)
            query_filter["deleted"] = {"$exists": False}
            await collection.update_many(query_filter, {"$set": {"deleted": dt}})

    async def _get_subgroups(
        self, network: str, group_uids: List[str], dt: datetime
    ) -> List[str]:
        collection = self._get_collection(network, "groups")
        projection = {"_id": False, "uid": True}
        query_filter = {}
        query_filter["created"] = {"$lte": dt}
        query_filter["$or"] = [
            {"deleted": {"$gt": dt}},
            {"deleted": {"$exists": False}},
        ]
        joined_group_uids = set(group_uids)
        new_uids = joined_group_uids
        while new_uids:
            query_filter["group_uid"] = {"$in": list(new_uids)}
            cursor = collection.find(filter=query_filter, projection=projection)
            found_groups = await cursor.to_list(None)
            found_group_uids = {g["uid"] for g in found_groups}
            new_uids = found_group_uids - joined_group_uids
            joined_group_uids |= new_uids

        return list(joined_group_uids)

    @staticmethod
    def _check_for_duplicate_uids(elements: List[Dict]):
        if len(elements) < 2:
            return
        uids = set()
        duplicate_uids = set()
        for e in elements:
            uid = e["uid"]
            if uid in uids:
                duplicate_uids.add(uid)
            uids.add(uid)
        if duplicate_uids:
            raise ValueError(f"Duplicate UIDs {duplicate_uids}")
