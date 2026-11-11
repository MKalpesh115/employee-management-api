import pytest
from fastapi.testclient import TestClient

EMPLOYEE = {
    "employee_id": 1,
    "name": "Taylor Smith",
    "email": "taylor@example.com",
    "department": "Engineering",
    "salary": 72000.0,
    "designation": "Developer",
}


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("POST", "/employees", EMPLOYEE),
        ("GET", "/employees", None),
        ("GET", "/employees/1", None),
        ("PUT", "/employees/1", EMPLOYEE),
        ("DELETE", "/employees/1", None),
    ],
)
def test_unauthorized_employee_access_is_rejected(
    client: TestClient,
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    response = client.request(method, path, json=body)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_bearer_token_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get(
        "/employees",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )

    assert response.status_code == 401


def test_employee_creation_and_retrieval(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    created = client.post("/employees", json=EMPLOYEE, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["employee_id"] == EMPLOYEE["employee_id"]

    retrieved = client.get("/employees/1", headers=auth_headers)
    assert retrieved.status_code == 200
    assert retrieved.json()["email"] == EMPLOYEE["email"]

    all_employees = client.get("/employees", headers=auth_headers)
    assert all_employees.status_code == 200
    assert len(all_employees.json()) == 1


def test_employee_update(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client.post("/employees", json=EMPLOYEE, headers=auth_headers)
    updated = {**EMPLOYEE, "name": "Taylor Jones", "salary": 80000.0}

    response = client.put("/employees/1", json=updated, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Taylor Jones"
    assert response.json()["salary"] == 80000.0


def test_employee_deletion(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client.post("/employees", json=EMPLOYEE, headers=auth_headers)

    response = client.delete("/employees/1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Employee deleted successfully"
    assert client.get("/employees/1", headers=auth_headers).status_code == 404


def test_employee_not_found(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/employees/999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


def test_invalid_employee_data_returns_validation_error(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    invalid_employee = {**EMPLOYEE, "salary": 0}

    response = client.post(
        "/employees",
        json=invalid_employee,
        headers=auth_headers,
    )

    assert response.status_code == 422
