import os
import sys

# Ensure the bundled dependencies/ folder is on the path when running in Lambda.
# Guarded so local dev / pytest uses the venv packages instead.
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):  # pragma: no cover
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dependencies"))

from fastapi import FastAPI
from mangum import Mangum

from users.api.v1.user_routes import router as user_router
from users.middleware.metrics import MetricsMiddleware

app = FastAPI(title="User Service", version="1.0.0")

app.add_middleware(MetricsMiddleware)
app.include_router(user_router, prefix="/api/v1")

# Mangum wraps the ASGI app so AWS Lambda / API Gateway can invoke it
handler = Mangum(app)
