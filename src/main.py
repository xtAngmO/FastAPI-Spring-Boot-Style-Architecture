from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.configs.config import get_settings
from src.configs.database_config import MongoDB
from src.controllers import auth_controller, user_controller
from src.exceptions.base_error import BaseError
from src.utils.banner import Banner

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    Banner().print_banner()
    await MongoDB().ensure_collections()
    yield
    await MongoDB().close_connection()


app = FastAPI(
    title="FastAPI",
    description="A FastAPI application architecture",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, prefix=settings.API_PREFIX, tags=["Authentication"])
app.include_router(user_controller.router, prefix=settings.API_PREFIX, tags=["Users"])


@app.exception_handler(BaseError)
async def base_error_handler(request: Request, exc: BaseError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "code": 500},
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to FastAPI"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "developer",
    )
