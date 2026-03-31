import uuid
from datetime import date

BASE_URL = "https://r1pbwtumcj.execute-api.us-east-1.amazonaws.com/dev/"

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
