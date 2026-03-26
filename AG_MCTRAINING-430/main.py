from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI
from prometheus_client import make_asgi_app
from common.metrics import MetricsMiddleware
import time

from update_user.router import router as update_user_router
from create_user.router import router as create_user_router
from delete_user.router import router as delete_user_router
from get_user.router import router as get_user_router 

app = FastAPI()
app.add_middleware(MetricsMiddleware)
app.include_router(create_user_router)
app.include_router(get_user_router)
app.include_router(update_user_router)
app.include_router(delete_user_router)

# Expose /metrics for Prometheus to scrape
app.mount("/metrics", make_asgi_app())