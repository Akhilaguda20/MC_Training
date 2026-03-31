"""
tests/test_config.py

Covers: users/core/config.py — all four Settings properties.
Each property reads from os.environ on every access (lazy @property),
so monkeypatching env vars is sufficient to hit every branch.
"""

import pytest

from users.core.config import settings


class TestSettings:
    def test_table_name_reads_from_env(self, monkeypatch):
        monkeypatch.setenv("TABLE_NAME", "custom-table")
        assert settings.TABLE_NAME == "custom-table"

    def test_event_bus_name_reads_from_env(self, monkeypatch):
        monkeypatch.setenv("EVENT_BUS_NAME", "custom-bus")
        assert settings.EVENT_BUS_NAME == "custom-bus"

    def test_event_bus_name_default_when_not_set(self, monkeypatch):
        monkeypatch.delenv("EVENT_BUS_NAME", raising=False)
        assert settings.EVENT_BUS_NAME == "user-events-bus"

    def test_localstack_url_reads_from_env(self, monkeypatch):
        monkeypatch.setenv("LOCALSTACK_URL", "http://localhost:4566")
        assert settings.LOCALSTACK_URL == "http://localhost:4566"

    def test_localstack_url_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("LOCALSTACK_URL", raising=False)
        assert settings.LOCALSTACK_URL is None

    def test_aws_region_reads_from_env(self, monkeypatch):
        monkeypatch.setenv("AWS_REGION", "eu-west-1")
        assert settings.AWS_REGION == "eu-west-1"

    def test_aws_region_default_when_not_set(self, monkeypatch):
        monkeypatch.delenv("AWS_REGION", raising=False)
        assert settings.AWS_REGION == "us-east-1"
