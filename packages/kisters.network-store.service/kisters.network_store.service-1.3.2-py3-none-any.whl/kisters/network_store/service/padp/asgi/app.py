from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import ORJSONResponse
from starlette.responses import RedirectResponse

from kisters.network_store.service.sadp.mongodb import NetworkStore

from .routers.networks import get_networks_router
from .routers.schemas import get_schemas_router
from .routers.viewer import get_viewer_router
from .settings import NetworkStoreAPIEnvironmentVariables


def create_app(network_store: NetworkStore | None = None, **kwargs) -> FastAPI:
    settings = NetworkStoreAPIEnvironmentVariables(**kwargs)
    network_store = network_store or NetworkStore()
    api_path = settings.api_path

    app = FastAPI(
        title="Network Store REST API",
        description="Storage service for directed graph infrastructure networks",
        docs_url=None if settings.enable_viewer else f"{api_path}/docs",
        redoc_url=f"{api_path}/redoc",
        openapi_url=f"{api_path}/openapi.json",
        default_response_class=ORJSONResponse,
    )

    if settings.enable_static_assets or settings.enable_viewer:
        from fastapi.staticfiles import StaticFiles

        # static asssets are required by the viewer
        static = Path(__file__).parent.resolve() / "static"
        app.mount("/static", StaticFiles(directory=static), name="static")

    dependencies = []

    if settings.enable_access_control:
        from kisters.water.operational.access_control.fastapi import TokenAuthenticator

        authenticator = TokenAuthenticator(
            allowed_origin=f"{settings.deployment_url}{api_path}/*"
        )
        dependencies.append(Depends(authenticator))

    networks = get_networks_router(network_store)
    app.include_router(
        networks,
        prefix=f"{api_path}/networks",
        tags=["networks"],
        dependencies=dependencies,
    )

    schemas = get_schemas_router()
    app.include_router(
        schemas,
        prefix=f"{api_path}/schemas",
        tags=["schemas"],
        dependencies=dependencies,
    )

    if settings.enable_viewer:
        viewer = get_viewer_router(network_store)
        app.include_router(
            viewer,
            prefix=f"{api_path}",
            tags=["viewer"],
            dependencies=dependencies,
        )

        @app.get(f"{api_path}/docs", include_in_schema=False)
        async def custom_swagger_ui_html():
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app.title + " - Swagger UI",
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="/static/swagger-ui-bundle.js",
                swagger_css_url="/static/swagger-ui.css",
            )

    @app.get("/", include_in_schema=False)
    async def docs_redirect_root():
        return RedirectResponse(url=f"{api_path}/docs")

    @app.get(api_path, include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url=f"{api_path}/docs")

    return app
