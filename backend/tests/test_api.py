from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def reviewed_bill(**overrides):
    payload = {
        "items": [
            {
                "id": "meal",
                "name": "Meal",
                "quantity": 2,
                "unit_price": 5000,
                "total_price": 10000,
            }
        ],
        "subtotal": 10000,
        "discount": 0,
        "service_charge": 0,
        "tax": 0,
        "printed_total": 10000,
    }
    payload.update(overrides)
    return payload


def test_validate_endpoint_accepts_valid_bill():
    response = client.post("/validate", json=reviewed_bill())
    assert response.status_code == 200
    assert response.json()["status"] == "valid"
    assert response.json()["calculated_total"] == 10000


def test_validate_endpoint_reports_invalid_bill():
    response = client.post("/validate", json=reviewed_bill(printed_total=11000))
    assert response.status_code == 200
    assert response.json()["status"] == "warning"
    assert response.json()["difference"] == 1000


def test_calculate_endpoint_accepts_valid_bill():
    response = client.post(
        "/calculate",
        json={
            "bill": reviewed_bill(),
            "people": ["Yash"],
            "assignments": {"meal": ["Yash"]},
        },
    )
    assert response.status_code == 200
    assert response.json()["people"]["Yash"]["total"] == 10000
    assert response.json()["difference"] == 0


def test_calculate_endpoint_rejects_invalid_item_arithmetic():
    payload = reviewed_bill(
        items=[
            {
                "id": "meal",
                "name": "Meal",
                "quantity": 3,
                "unit_price": 5000,
                "total_price": 10000,
            }
        ]
    )
    response = client.post(
        "/calculate",
        json={"bill": payload, "people": ["Yash"], "assignments": {"meal": ["Yash"]}},
    )
    assert response.status_code == 422
    assert any("total mismatch" in message for message in response.json()["detail"])


def test_calculate_endpoint_rejects_invalid_subtotal():
    response = client.post(
        "/calculate",
        json={
            "bill": reviewed_bill(subtotal=9000, printed_total=9000),
            "people": ["Yash"],
            "assignments": {"meal": ["Yash"]},
        },
    )
    assert response.status_code == 422
    assert any("Subtotal mismatch" in message for message in response.json()["detail"])


def test_calculate_endpoint_allows_printed_total_warning():
    response = client.post(
        "/calculate",
        json={
            "bill": reviewed_bill(printed_total=11000),
            "people": ["Yash"],
            "assignments": {"meal": ["Yash"]},
        },
    )
    assert response.status_code == 200
    assert response.json()["people"]["Yash"]["total"] == 10000
    assert response.json()["validation"]["status"] == "warning"
    assert any(
        "Printed total mismatch" in message
        for message in response.json()["validation"]["messages"]
    )


def test_calculate_endpoint_splits_shared_item():
    payload = reviewed_bill(
        items=[
            {
                "id": "shared",
                "name": "Shared",
                "quantity": 1,
                "unit_price": 10001,
                "total_price": 10001,
            }
        ],
        subtotal=10001,
        printed_total=10001,
    )
    response = client.post(
        "/calculate",
        json={
            "bill": payload,
            "people": ["Yash", "Rahul"],
            "assignments": {"shared": ["Yash", "Rahul"]},
        },
    )
    assert response.status_code == 200
    assert [response.json()["people"][name]["subtotal"] for name in ["Yash", "Rahul"]] == [5001, 5000]


def test_calculate_endpoint_rejects_invalid_assignment():
    response = client.post(
        "/calculate",
        json={
            "bill": reviewed_bill(),
            "people": ["Yash"],
            "assignments": {"meal": ["Unknown"]},
        },
    )
    assert response.status_code == 422
    assert "invalid assignment" in response.json()["detail"]


def test_invalid_request_payload_returns_422():
    response = client.post("/validate", json={"items": "not-a-list"})
    assert response.status_code == 422


def test_calculate_endpoint_rejects_malformed_request():
    response = client.post(
        "/calculate",
        json={"bill": {"items": "not-a-list"}, "people": ["Yash"], "assignments": {}},
    )
    assert response.status_code == 422
