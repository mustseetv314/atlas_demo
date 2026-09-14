def test_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "IT Asset Inventory" in response.text
    assert "SRV-TEST" in response.text


def test_liveness(client):
    assert client.get("/health/live").json() == {"status": "alive", "application": "Atlas"}


def test_readiness_connected(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_readiness_disconnected(client, monkeypatch):
    monkeypatch.setattr("app.main.check_database", lambda: False)
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["database"] == "disconnected"


def test_info_does_not_expose_database_configuration(client):
    data = client.get("/api/info").json()
    assert data == {"application": "Atlas", "version": "1.0.0", "environment": "production"}


def test_assets_crud_and_not_found(client):
    assert len(client.get("/api/assets").json()) == 1
    payload = {"asset_tag": "LAP-NEW", "name": "New Laptop", "asset_type": "Laptop", "owner": "Support", "environment": "Corporate", "status": "Active", "location": "Chicago", "operating_system": "Windows 11"}
    created = client.post("/api/assets", json=payload)
    assert created.status_code == 201
    asset_id = created.json()["id"]
    payload["status"] = "Maintenance"
    assert client.put(f"/api/assets/{asset_id}", json=payload).json()["status"] == "Maintenance"
    assert client.delete(f"/api/assets/{asset_id}").status_code == 204
    assert client.get(f"/api/assets/{asset_id}").status_code == 404


def test_search_and_filters(client):
    assert len(client.get("/api/assets", params={"search": "Test Lab", "environment": "Test", "status_filter": "Active"}).json()) == 1
    assert client.get("/api/assets", params={"search": "missing"}).json() == []


def test_input_validation(client):
    response = client.post("/api/assets", json={"asset_tag": ""})
    assert response.status_code == 422


def test_unknown_route(client):
    assert client.get("/not-a-route").status_code == 404
