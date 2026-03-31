import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from payroll.api.v1.payroll_routes import router as payroll_router
from payroll.middleware.metrics import MetricsMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Payroll Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetricsMiddleware)
app.include_router(payroll_router)

# Mangum wraps the ASGI app so AWS Lambda / API Gateway can invoke it
handler = Mangum(app, lifespan="off")
