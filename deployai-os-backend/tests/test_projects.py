def test_create_and_list_project(register, client):
    headers = register(organization="ProjOrg")
    create = client.post(
        "/projects",
        json={"name": "Test Deployment", "customerName": "Test Customer", "environment": "development"},
        headers=headers,
    )
    assert create.status_code == 201
    project = create.json()
    assert project["name"] == "Test Deployment"
    assert project["status"] == "active"
    assert project["currentStage"] == "discovery"

    listing = client.get("/projects", headers=headers)
    assert listing.status_code == 200
    assert any(p["id"] == project["id"] for p in listing.json())


def test_get_nonexistent_project_returns_404(register, client):
    headers = register(organization="ProjOrg2")
    response = client.get("/projects/does-not-exist", headers=headers)
    assert response.status_code == 404


def test_create_project_requires_auth(client):
    response = client.post(
        "/projects", json={"name": "X", "customerName": "Y", "environment": "development"}
    )
    assert response.status_code == 401
