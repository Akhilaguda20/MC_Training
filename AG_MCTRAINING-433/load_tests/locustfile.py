from locust import HttpUser, between, events

from load_tests.payroll_tasks import PayrollTasks
from load_tests.users_tasks import UserTasks


# ── Simulated user types ───────────────────────────────────────────────────────

LOCALSTACK_HOST = "http://localhost:4566/restapis/cvewbmgixp/local/_user_request_"


class UserServiceLoad(HttpUser):
    """
    Simulates traffic against the Users Lambda (users.main.handler).
    Routes: /api/v1/users/*
    """

    host = LOCALSTACK_HOST
    tasks = [UserTasks]
    wait_time = between(0.5, 2)
    weight = 3                   # 3x more user-service traffic than payroll


class PayrollServiceLoad(HttpUser):
    """
    Simulates traffic against the Payroll Lambda (payroll.main.handler).
    Routes: /api/v1/payroll/*
    """

    host = LOCALSTACK_HOST       
    tasks = [PayrollTasks]
    wait_time = between(1, 3)
    weight = 1

# ── Pass/fail thresholds ───────────────────────────────────────────────────────

@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.stats.total
    failed = False

    if stats.fail_ratio > 0.01:
        print(f"[FAIL] Error rate {stats.fail_ratio:.2%} exceeds threshold of 1%")
        failed = True

    p95 = stats.get_response_time_percentile(0.95)
    if p95 and p95 > 500:
        print(f"[FAIL] p95 latency {p95:.0f}ms exceeds threshold of 500ms")
        failed = True

    if failed:
        environment.process_exit_code = 1


# ── Request error logging ──────────────────────────────────────────────────────

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response,
               context, exception, **kwargs):
    if exception:
        print(f"[ERROR] {request_type} {name} — {exception}")
    elif response and response.status_code >= 500:
        print(f"[5xx]   {request_type} {name} — {response.status_code} in {response_time:.0f}ms")
