import logging

from locust import TaskSet, task

from load_tests.config import make_user_payload

logger = logging.getLogger(__name__)

BASE = "/api/v1"


class UserTasks(TaskSet):
    """
    Simulates realistic user service traffic:
      - get_user    → weight 5  (heavy read)
      - create_user → weight 3  (moderate write)
      - update_user → weight 2  (occasional update)
      - delete_user → weight 1  (rare delete)
    """

    def on_start(self):
        """Runs once when a simulated user starts. Seed the ID pool."""
        self.created_user_ids: list = []
        self._create_seed_user()

    def _create_seed_user(self):
        payload = make_user_payload()
        with self.client.post(
            f"{BASE}/users",
            json=payload,
            name="POST /api/v1/users [seed]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                user_id = resp.json().get("userId")
                if user_id:
                    self.created_user_ids.append(user_id)
            else:
                resp.failure(f"Seed user creation failed: {resp.status_code}")

    # ── Tasks ─────────────────────────────────────────────────────────────────

    @task(5)
    def get_user(self):
        """GET /api/v1/users/{userId} — most frequent read"""
        if not self.created_user_ids:
            self._create_seed_user()
            return

        user_id = self.created_user_ids[-1]
        with self.client.get(
            f"{BASE}/users/{user_id}",
            name="GET /api/v1/users/{userId}",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 404:
                resp.success()
            else:
                resp.failure(f"Unexpected status: {resp.status_code}")

    @task(3)
    def create_user(self):
        """POST /api/v1/users — frequent write"""
        payload = make_user_payload()
        with self.client.post(
            f"{BASE}/users",
            json=payload,
            name="POST /api/v1/users",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                user_id = resp.json().get("userId")
                if user_id:
                    self.created_user_ids.append(user_id)
                resp.success()
            else:
                resp.failure(f"Create user failed: {resp.status_code} — {resp.text}")

    @task(2)
    def update_user(self):
        """PUT /api/v1/users/{userId} — occasional update"""
        if not self.created_user_ids:
            return

        user_id = self.created_user_ids[-1]
        uid = user_id[:8]
        with self.client.put(
            f"{BASE}/users/{user_id}",
            json={"name": f"Updated {uid}", "email": f"updated_{uid}@loadtest.com"},
            name="PUT /api/v1/users/{userId}",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Update user failed: {resp.status_code}")

    @task(1)
    def delete_user(self):
        """DELETE /api/v1/users/{userId} — rare"""
        if not self.created_user_ids:
            return

        user_id = self.created_user_ids.pop()
        with self.client.delete(
            f"{BASE}/users/{user_id}",
            name="DELETE /api/v1/users/{userId}",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Delete user failed: {resp.status_code}")
