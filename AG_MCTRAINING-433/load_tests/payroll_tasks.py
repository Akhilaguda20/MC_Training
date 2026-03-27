import logging
import uuid

from locust import TaskSet, task

from load_tests.config import make_payroll_payload, make_payroll_update_payload

logger = logging.getLogger(__name__)

BASE = "/api/v1"


class PayrollTasks(TaskSet):
    """
    Simulates realistic payroll service traffic:
      - get_payroll          → weight 5  (heavy read by ID)
      - list_payroll_by_user → weight 4  (frequent list by user)
      - create_payroll       → weight 2  (moderate write)
      - update_payroll       → weight 1  (occasional update)
      - delete_payroll       → weight 1  (rare delete)
    """

    # pool of {"user_id": ..., "payroll_id": ...} entries for read tasks
    pool: list = []

    def on_start(self):
        """Runs once when a simulated user starts. Seed the pool."""
        self._seed_payroll_record()

    def _seed_payroll_record(self):
        """Create a payroll record to seed read tasks.

        The payroll service does not validate whether the userId exists in the
        users service, so we generate a UUID directly — no cross-service call
        needed. This keeps PayrollTasks fully self-contained on port 8001.
        """
        user_id = str(uuid.uuid4())
        payroll_resp = self.client.post(
            f"{BASE}/payroll",
            json=make_payroll_payload(user_id),
            name="POST /api/v1/payroll [seed]",
        )
        if payroll_resp.status_code == 201:
            payroll_id = payroll_resp.json().get("payrollId")
            if payroll_id:
                self.pool.append({"user_id": user_id, "payroll_id": payroll_id})

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task(5)
    def get_payroll(self):
        """GET /api/v1/payroll/{payrollId}"""
        if not self.pool:
            self._seed_payroll_record()
            return

        entry = self.pool[-1]
        with self.client.get(
            f"{BASE}/payroll/{entry['payroll_id']}",
            name="GET /api/v1/payroll/{payrollId}",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(4)
    def list_payroll_by_user(self):
        """GET /api/v1/payroll/user/{userId}"""
        if not self.pool:
            return

        user_id = self.pool[-1]["user_id"]
        with self.client.get(
            f"{BASE}/payroll/user/{user_id}",
            name="GET /api/v1/payroll/user/{userId}",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"List payroll failed: {resp.status_code}")

    @task(2)
    def create_payroll(self):
        """POST /api/v1/payroll"""
        if not self.pool:
            return

        user_id = self.pool[-1]["user_id"]
        with self.client.post(
            f"{BASE}/payroll",
            json=make_payroll_payload(user_id),
            name="POST /api/v1/payroll",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                payroll_id = resp.json().get("payrollId")
                if payroll_id:
                    self.pool.append({"user_id": user_id, "payroll_id": payroll_id})
                resp.success()
            else:
                resp.failure(f"Create payroll failed: {resp.status_code} — {resp.text}")

    @task(1)
    def update_payroll(self):
        """PUT /api/v1/payroll/{payrollId}"""
        if not self.pool:
            return

        entry = self.pool[-1]
        with self.client.put(
            f"{BASE}/payroll/{entry['payroll_id']}",
            json=make_payroll_update_payload(),
            name="PUT /api/v1/payroll/{payrollId}",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Update payroll failed: {resp.status_code}")

    @task(1)
    def delete_payroll(self):
        """DELETE /api/v1/payroll/{payrollId}"""
        if not self.pool:
            return

        entry = self.pool.pop()
        with self.client.delete(
            f"{BASE}/payroll/{entry['payroll_id']}",
            name="DELETE /api/v1/payroll/{payrollId}",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Delete payroll failed: {resp.status_code}")
