
def test_place_order_without_login(client):
    response = client.post(
        "/api/orders",
        json={
            "items": [],
            "customer_name": "Deepak",
            "phone": "9876543210",
            "address": "Mysuru"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"


def test_my_orders_without_login(client):
    response = client.get("/api/my-orders")

    assert response.status_code == 401
    assert response.json["error"] == "Please login first"
