"""
tests/test_utils.py

Covers: payroll/utils/response.py — build_response().
"""

import json

from payroll.utils.response import build_response


class TestBuildResponse:
    def test_status_code_is_preserved(self):
        result = build_response(201, {"message": "created"})
        assert result["statusCode"] == 201

    def test_content_type_header_is_json(self):
        result = build_response(200, {})
        assert result["headers"]["Content-Type"] == "application/json"

    def test_cors_header_allows_all_origins(self):
        result = build_response(200, {})
        assert result["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_body_is_json_serialised_string(self):
        body = {"payrollId": "p-1", "baseSalary": "5000"}
        result = build_response(200, body)
        assert result["body"] == json.dumps(body)
