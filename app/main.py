from fastapi import FastAPI

from app.api.router import api_router
from app.middleware.error_handlers import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="ConstructProcure AI API", version="0.1.0")
    app.include_router(api_router)
    register_exception_handlers(app)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
