import asyncio
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings


class MongoDBMotorClientEnvironmentVariables(BaseSettings):
    appname: str = "NetworkStore"
    host: str = "mongodb://localhost:27017"
    username: Optional[str] = None
    password: Optional[str] = None
    network_database_prefix = "network_store_"

    class Config:
        env_prefix = "mongodb_"
        env_file = "kisters_water.env"

    def create_client(
        self, io_loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> AsyncIOMotorClient:
        config = {"appname": self.appname, "tz_aware": True}
        if io_loop:
            config["io_loop"] = io_loop
        config["host"] = self.host

        # Provide Login Credentials (if any)
        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password

        # Initialize the MongoDB client
        return AsyncIOMotorClient(**config)
