import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from users.api.v1.user_routes import router as user_router
from users.middleware.metrics import MetricsMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="User Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetricsMiddleware)
app.include_router(user_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Mangum wraps the ASGI app so AWS Lambda / API Gateway can invoke it
handler = Mangum(app, lifespan="off")
