import time

from aws_embedded_metrics import metric_scope
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match


@metric_scope
async def _emit_metrics(
    namespace: str, method: str, route: str, latency_ms: float, status: int, metrics
):
    metrics.set_namespace(namespace)
    # set_dimensions replaces Lambda default dimensions (FunctionName, LogGroup, etc.)
    # so the only CloudWatch dimensions are Method + Route, giving clean per-route series.
    metrics.set_dimensions({"Method": method, "Route": route})
    metrics.put_metric("RequestCount", 1, "Count")
    metrics.put_metric("Latency", latency_ms, "Milliseconds")
    metrics.put_metric("Is4xxError", 1 if 400 <= status < 500 else 0, "Count")
    metrics.put_metric("Is5xxError", 1 if status >= 500 else 0, "Count")


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000

        route = self._resolve_route(request)
        await _emit_metrics(
            "PayrollService/Api", request.method, route, latency_ms, response.status_code
        )
        return response

    def _resolve_route(self, request: Request) -> str:
        """Return the matched route template path (e.g. /api/v1/payroll/{payroll_id})
        instead of the concrete URL, to avoid high-cardinality metric dimensions."""
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return getattr(route, "path", request.url.path)
        return request.url.path
