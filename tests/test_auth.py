def test_register_missing_fields(client):
    response = client.post(
        "/api/register",
        json={}
    )

    assert response.status_code == 400
    assert response.json["error"] == "All fields are required"


def test_register_short_password(client):
    response = client.post(
        "/api/register",
        json={
            "name": "Deepak",
            "email": "deepak@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 400
    assert "at least 8 characters" in response.json["error"]


def test_login_missing_fields(client):
    response = client.post(
        "/api/login",
        json={}
    )

    assert response.status_code == 400


def test_session_without_login(client):
    response = client.get("/api/session")

    assert response.status_code == 401
    assert response.json["error"] == "Not logged in"


def test_logout(client):
    with client.session_transaction() as session:
        session["user_id"] = 1

    response = client.post("/api/logout")

    assert response.status_code == 200
    assert response.json["message"] == "Logged out successfully"

    session_response = client.get("/api/session")
    assert session_response.status_code == 401
