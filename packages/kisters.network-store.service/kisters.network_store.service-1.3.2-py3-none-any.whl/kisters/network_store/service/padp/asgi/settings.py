from pydantic import BaseSettings


class NetworkStoreAPIEnvironmentVariables(BaseSettings):
    class Config:
        env_file = "kisters_water.env"
        env_prefix = "network_store_"

    api_path: str = "/network-store"
    deployment_url: str = ""
    enable_access_control: bool = False
    enable_static_assets: bool = False
    enable_viewer: bool = True
