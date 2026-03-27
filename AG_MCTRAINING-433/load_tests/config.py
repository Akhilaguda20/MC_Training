import uuid
from datetime import date

LOCALSTACK_BASE_URL = "http://localhost:4566/restapis/cvewbmgixp/local/_user_request_"

def make_user_payload() -> dict:
    uid = uuid.uuid4().hex[:8]
    return {
        "name": f"Test User {uid}",
        "email": f"user_{uid}@loadtest.com",
    }


def make_payroll_payload(user_id: str) -> dict:
    return {
        "userId": user_id,
        "baseSalary": "75000.00",
        "bonus": "5000.00",
        "deductions": "1200.00",
        "currency": "USD",
        "effectiveDate": str(date.today()),
    }


def make_payroll_update_payload() -> dict:
    return {
        "bonus": "6000.00",
        "deductions": "1300.00",
    }
