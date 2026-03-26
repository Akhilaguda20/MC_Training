"""
tests/test_payroll.py

Tests at two levels:
  1. Service unit tests — PayrollService + in-memory fakes, zero HTTP/AWS.
  2. Route integration tests — FastAPI TestClient + dependency_overrides,
     zero boto3 calls.

No patching. No mocks. Pure dependency injection.
"""

import pytest
from fastapi.testclient import TestClient

from payroll.core.dependencies import get_payroll_service
from payroll.main import app
from payroll.repositories.dynamodb import DynamoDBPayrollRepository
from payroll.services.payroll_service import PayrollService
from payroll.tests.conftest import InMemoryPayrollRepository


# Helpers                                                                      #

def make_service(repo=None) -> PayrollService:
    """Build a PayrollService backed entirely by in-memory fakes."""
    return PayrollService(repo=repo or InMemoryPayrollRepository())


# 1. PayrollService — unit tests (no FastAPI, no HTTP)                        #

class TestPayrollServiceCreate:
    def test_generates_uuid_when_payroll_id_not_provided(self):
        repo = InMemoryPayrollRepository()
        service = make_service(repo=repo)

        payroll_id = service.create_payroll({
            "userId": "u-1",
            "baseSalary": "5000",
            "effectiveDate": "2026-01-01",
        })

        assert payroll_id is not None
        assert len(payroll_id) == 36  # UUID4 format
        assert repo.get(payroll_id) is not None

    def test_uses_provided_payroll_id(self):
        repo = InMemoryPayrollRepository()
        service = make_service(repo=repo)

        payroll_id = service.create_payroll({
            "payrollId": "p-001",
            "userId": "u-1",
            "baseSalary": "5000",
            "effectiveDate": "2026-01-01",
        })

        assert payroll_id == "p-001"
        assert repo.get("p-001")["userId"] == "u-1"


class TestPayrollServiceGet:
    def test_returns_record_when_exists(self):
        repo = InMemoryPayrollRepository()
        service = make_service(repo=repo)
        service.create_payroll({
            "payrollId": "p-1",
            "userId": "u-1",
            "baseSalary": "5000",
            "effectiveDate": "2026-01-01",
        })

        result = service.get_payroll("p-1")

        assert result is not None
        assert result["payrollId"] == "p-1"

    def test_returns_none_when_not_found(self):
        service = make_service()
        assert service.get_payroll("nonexistent") is None


class TestPayrollServiceListByUser:
    def test_returns_all_records_for_user(self):
        repo = InMemoryPayrollRepository()
        service = make_service(repo=repo)
        service.create_payroll({"payrollId": "p-1", "userId": "u-1", "baseSalary": "5000", "effectiveDate": "2026-01-01"})
        service.create_payroll({"payrollId": "p-2", "userId": "u-1", "baseSalary": "6000", "effectiveDate": "2026-06-01"})
        service.create_payroll({"payrollId": "p-3", "userId": "u-2", "baseSalary": "4000", "effectiveDate": "2026-01-01"})

        results = service.list_payroll_by_user("u-1")

        assert len(results) == 2
        assert all(r["userId"] == "u-1" for r in results)

    def test_returns_empty_list_when_no_records(self):
        service = make_service()
        assert service.list_payroll_by_user("u-nobody") == []


class TestPayrollServiceUpdate:
    def test_returns_true_and_updates_record(self):
        repo = InMemoryPayrollRepository()
        service = make_service(repo=repo)
        service.create_payroll({"payrollId": "p-1", "userId": "u-1", "baseSalary": "5000", "effectiveDate": "2026-01-01"})

        result = service.update_payroll("p-1", {"baseSalary": "6000"})

        assert result is True
        assert repo.get("p-1")["baseSalary"] == "6000"

    def test_returns_false_when_record_not_found(self):
        service = make_service()
        result = service.update_payroll("nonexistent", {"baseSalary": "6000"})
        assert result is False


class TestPayrollServiceDelete:
    def test_removes_record_from_repo(self):
        repo = InMemoryPayrollRepository()
        service = make_service(repo=repo)
        service.create_payroll({"payrollId": "p-del", "userId": "u-1", "baseSalary": "5000", "effectiveDate": "2026-01-01"})

        service.delete_payroll("p-del")

        assert repo.get("p-del") is None


# 2. DynamoDBPayrollRepository — unit tests with injected mock client         #

class TestDynamoDBPayrollRepository:
    def _repo(self, mock_client):
        return DynamoDBPayrollRepository(mock_client, "test-payroll-table")

    def test_create_calls_put_item(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        repo.create("p-1", {"userId": "u-1", "baseSalary": "5000", "bonus": "500", "deductions": "100", "currency": "USD", "effectiveDate": "2026-01-01"})

        mock_client.put_item.assert_called_once()
        call_kwargs = mock_client.put_item.call_args.kwargs
        assert call_kwargs["TableName"] == "test-payroll-table"
        assert call_kwargs["Item"]["payrollId"] == {"S": "p-1"}
        assert call_kwargs["Item"]["userId"] == {"S": "u-1"}
        assert call_kwargs["Item"]["baseSalary"] == {"N": "5000"}
        assert call_kwargs["Item"]["status"] == {"S": "ACTIVE"}

    def test_get_returns_flattened_dict_when_item_found(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.get_item.return_value = {
            "Item": {
                "payrollId":  {"S": "p-1"},
                "userId":     {"S": "u-1"},
                "baseSalary": {"N": "5000"},
                "status":     {"S": "ACTIVE"},
            }
        }
        repo = self._repo(mock_client)

        result = repo.get("p-1")

        assert result == {"payrollId": "p-1", "userId": "u-1", "baseSalary": "5000", "status": "ACTIVE"}

    def test_get_returns_none_when_item_not_found(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.get_item.return_value = {}
        repo = self._repo(mock_client)

        assert repo.get("missing") is None

    def test_list_by_user_calls_query_with_gsi(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.query.return_value = {"Items": []}
        repo = self._repo(mock_client)

        repo.list_by_user("u-1")

        mock_client.query.assert_called_once()
        call_kwargs = mock_client.query.call_args.kwargs
        assert call_kwargs["IndexName"] == "userId-index"
        assert call_kwargs["ExpressionAttributeValues"][":uid"] == {"S": "u-1"}

    def test_list_by_user_returns_flattened_items(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.query.return_value = {
            "Items": [
                {"payrollId": {"S": "p-1"}, "userId": {"S": "u-1"}, "baseSalary": {"N": "5000"}},
                {"payrollId": {"S": "p-2"}, "userId": {"S": "u-1"}, "baseSalary": {"N": "6000"}},
            ]
        }
        repo = self._repo(mock_client)

        result = repo.list_by_user("u-1")

        assert len(result) == 2
        assert result[0]["payrollId"] == "p-1"
        assert result[1]["baseSalary"] == "6000"

    def test_update_returns_true_when_item_exists(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        result = repo.update("p-1", {"baseSalary": "6000"})

        assert result is True
        mock_client.update_item.assert_called_once()

    def test_update_returns_false_on_conditional_check_failure(self, mocker):
        mock_client = mocker.MagicMock()
        mock_client.exceptions.ConditionalCheckFailedException = Exception
        mock_client.update_item.side_effect = Exception("ConditionalCheckFailed")
        repo = self._repo(mock_client)

        result = repo.update("nonexistent", {"baseSalary": "6000"})

        assert result is False

    def test_delete_calls_delete_item(self, mocker):
        mock_client = mocker.MagicMock()
        repo = self._repo(mock_client)

        repo.delete("p-1")

        mock_client.delete_item.assert_called_once_with(
            TableName="test-payroll-table",
            Key={"payrollId": {"S": "p-1"}},
        )


# 3. Route integration tests — FastAPI TestClient + dependency_overrides      #

@pytest.fixture
def client():
    """
    TestClient with dependency_overrides injecting in-memory fakes.
    No boto3, no network, no patching.
    """
    repo = InMemoryPayrollRepository()
    service = PayrollService(repo)

    app.dependency_overrides[get_payroll_service] = lambda: service
    yield TestClient(app), repo
    app.dependency_overrides.clear()


class TestCreatePayrollRoute:
    def test_returns_201_with_payroll_id(self, client):
        http, _ = client
        response = http.post("/api/v1/payroll", json={
            "userId": "u-1",
            "baseSalary": "5000",
            "effectiveDate": "2026-01-01",
        })
        assert response.status_code == 201
        assert "payrollId" in response.json()

    def test_uses_provided_payroll_id(self, client):
        http, repo = client
        response = http.post("/api/v1/payroll", json={
            "payrollId": "p-fixed",
            "userId": "u-1",
            "baseSalary": "5000",
            "effectiveDate": "2026-01-01",
        })
        assert response.status_code == 201
        assert response.json()["payrollId"] == "p-fixed"
        assert repo.get("p-fixed") is not None


class TestGetPayrollRoute:
    def test_returns_200_with_record(self, client):
        http, repo = client
        repo.create("p-get", {"userId": "u-1", "baseSalary": "5000", "effectiveDate": "2026-01-01"})

        response = http.get("/api/v1/payroll/p-get")

        assert response.status_code == 200
        assert response.json()["payrollId"] == "p-get"

    def test_returns_404_when_not_found(self, client):
        http, _ = client
        response = http.get("/api/v1/payroll/nobody")
        assert response.status_code == 404


class TestListPayrollByUserRoute:
    def test_returns_200_with_records_list(self, client):
        http, repo = client
        repo.create("p-1", {"userId": "u-list", "baseSalary": "5000", "effectiveDate": "2026-01-01"})
        repo.create("p-2", {"userId": "u-list", "baseSalary": "6000", "effectiveDate": "2026-06-01"})

        response = http.get("/api/v1/payroll/user/u-list")

        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == "u-list"
        assert len(data["records"]) == 2

    def test_returns_empty_list_when_no_records(self, client):
        http, _ = client
        response = http.get("/api/v1/payroll/user/u-nobody")
        assert response.status_code == 200
        assert response.json()["records"] == []


class TestUpdatePayrollRoute:
    def test_returns_200_when_record_updated(self, client):
        http, repo = client
        repo.create("p-upd", {"userId": "u-1", "baseSalary": "5000", "effectiveDate": "2026-01-01"})

        response = http.put("/api/v1/payroll/p-upd", json={"baseSalary": "6000"})

        assert response.status_code == 200
        assert response.json() == {"message": "Payroll record updated"}
        assert repo.get("p-upd")["baseSalary"] == "6000"

    def test_returns_404_when_record_not_found(self, client):
        http, _ = client
        response = http.put("/api/v1/payroll/nonexistent", json={"baseSalary": "6000"})
        assert response.status_code == 404


class TestDeletePayrollRoute:
    def test_returns_200_and_removes_record(self, client):
        http, repo = client
        repo.create("p-del", {"userId": "u-1", "baseSalary": "5000", "effectiveDate": "2026-01-01"})

        response = http.delete("/api/v1/payroll/p-del")

        assert response.status_code == 200
        assert repo.get("p-del") is None
