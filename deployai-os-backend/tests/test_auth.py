def test_register_creates_admin_for_new_organization(client):
    response = client.post(
        "/auth/register",
        json={"name": "Amina Rahman", "email": "amina@newco.example", "organization": "NewCo", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["role"] == "admin"
    assert body["tokenType"] == "bearer"
    assert body["accessToken"]


def test_second_user_joining_same_org_is_employee(register, client):
    register(email="first@shared.example", organization="Shared Co")
    response = client.post(
        "/auth/register",
        json={"name": "Second User", "email": "second@shared.example", "organization": "Shared Co", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["user"]["role"] == "employee"


def test_duplicate_email_is_rejected(client):
    payload = {"name": "A", "email": "dupe@example.com", "organization": "Org A", "password": "password123"}
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409


def test_login_with_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"name": "A", "email": "loginfail@example.com", "organization": "Org B", "password": "correct-password"},
    )
    response = client.post("/auth/login", json={"email": "loginfail@example.com", "password": "wrong-password"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(register, client):
    headers = register(email="whoami@example.com", organization="Org C")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "whoami@example.com"


def test_demo_login_works_with_no_seed_data(client):
    response = client.post("/auth/demo")
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
