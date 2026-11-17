
from unittest.mock import MagicMock


def test_get_products(client, monkeypatch):
    conn = MagicMock()
    cursor = MagicMock()

    conn.cursor.return_value.__enter__.return_value = cursor

    cursor.fetchall.return_value = [
        (1, "Laptop", "Test laptop", 55000.00, "laptop.jpg"),
        (2, "Mouse", "Wireless mouse", 500.00, "mouse.jpg")
    ]

    monkeypatch.setattr(
        "app.get_db",
        lambda: conn
    )

    response = client.get("/api/products")

    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["name"] == "Laptop"
    assert response.json[1]["name"] == "Mouse"
    assert response.json[0]["price"] == 55000.00

    conn.close.assert_called_once()
