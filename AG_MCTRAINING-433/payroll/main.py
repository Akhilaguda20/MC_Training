from fastapi import FastAPI
from mangum import Mangum

from payroll.api.v1.payroll_routes import router as payroll_router
from payroll.middleware.metrics import MetricsMiddleware

app = FastAPI(title="Payroll Service", version="1.0.0")

app.add_middleware(MetricsMiddleware)
app.include_router(payroll_router, prefix="/api/v1")

# Mangum wraps the ASGI app so AWS Lambda / API Gateway can invoke it
handler = Mangum(app)
