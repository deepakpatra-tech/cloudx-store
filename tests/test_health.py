
from unittest.mock import MagicMock


def test_health_database_connected(client, monkeypatch):
    conn = MagicMock()
    cursor = MagicMock()

    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.fetchone.return_value = (1,)

    monkeypatch.setattr(
        "app.get_db",
        lambda: conn
    )

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"
    assert response.json["database"] == "connected"
    conn.close.assert_called_once()


def test_health_database_disconnected(client, monkeypatch):
    monkeypatch.setattr(
        "app.get_db",
        lambda: (_ for _ in ()).throw(Exception("Database unavailable"))
    )

    response = client.get("/api/health")

    assert response.status_code == 500
    assert response.json["status"] == "unhealthy"
    assert response.json["database"] == "disconnected"
