"""
Integration tests for the FastAPI API endpoints.

Tests the full request/response cycle using FastAPI's TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store import task_store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the task store before each test."""
    task_store.clear()
    yield
    task_store.clear()


client = TestClient(app)


class TestHealthCheck:

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Task Agent API" in response.json()["message"]


class TestCreateTask:

    def test_create_calculator_task(self):
        response = client.post("/api/tasks", json={"input": "calculate 3 + 5"})
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert "8" in data["output"]
        assert data["tool_used"] == "CalculatorTool"
        assert len(data["execution_steps"]) >= 3

    def test_create_text_task(self):
        response = client.post("/api/tasks", json={"input": 'Convert "hello" to uppercase'})
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert "HELLO" in data["output"]

    def test_create_weather_task(self):
        response = client.post("/api/tasks", json={"input": "weather in London"})
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert "London" in data["output"]

    def test_empty_input_rejected(self):
        response = client.post("/api/tasks", json={"input": ""})
        assert response.status_code == 422  # Validation error

    def test_missing_input_rejected(self):
        response = client.post("/api/tasks", json={})
        assert response.status_code == 422


class TestListTasks:

    def test_empty_list(self):
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_after_creating(self):
        client.post("/api/tasks", json={"input": "3 + 5"})
        client.post("/api/tasks", json={"input": "weather in Tokyo"})
        response = client.get("/api/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2


class TestGetTask:

    def test_get_existing_task(self):
        create_response = client.post("/api/tasks", json={"input": "3 + 5"})
        task_id = create_response.json()["id"]

        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_get_nonexistent_task(self):
        response = client.get("/api/tasks/nonexistent-id")
        assert response.status_code == 404


class TestExportTasks:

    def test_export_empty(self):
        response = client.get("/api/tasks/export")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_export_with_data(self):
        client.post("/api/tasks", json={"input": "3 + 5"})
        response = client.get("/api/tasks/export")
        assert response.status_code == 200
        assert response.json()["count"] == 1


class TestListTools:

    def test_list_tools(self):
        response = client.get("/api/tools")
        assert response.status_code == 200
        tools = response.json()
        assert len(tools) == 3
        names = [t["name"] for t in tools]
        assert "CalculatorTool" in names
