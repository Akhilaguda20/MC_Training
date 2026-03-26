from fastapi import FastAPI
from mangum import Mangum

from users.api.v1.user_routes import router as user_router
from users.middleware.metrics import MetricsMiddleware

app = FastAPI(title="User Service", version="1.0.0")

app.add_middleware(MetricsMiddleware)
app.include_router(user_router, prefix="/api/v1")

# Mangum wraps the ASGI app so AWS Lambda / API Gateway can invoke it
handler = Mangum(app)
