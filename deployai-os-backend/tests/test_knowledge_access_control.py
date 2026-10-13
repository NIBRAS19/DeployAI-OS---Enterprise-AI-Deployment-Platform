"""The flagship test: ADR-003 (authorize before retrieval, not after) has to
actually hold, not just be documented. Every test here exercises the real
upload -> embed -> authorize -> retrieve pipeline end to end, with no
mocking of the RAG or access-control logic itself.
"""


def _create_project(client, headers):
    response = client.post(
        "/projects",
        json={"name": "Secure Project", "customerName": "Secure Customer", "environment": "production"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _upload(client, headers, project_id, filename, content, department, classification):
    response = client.post(
        f"/projects/{project_id}/knowledge/upload",
        files={"file": (filename, content.encode("utf-8"), "text/plain")},
        data={"department": department, "classification": classification},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


RESTRICTED_CONTENT = (
    "Executive salary bands range from 800000 to 1500000 per year, reviewed annually by the board "
    "compensation committee alongside bonus and equity targets."
)
PUBLIC_CONTENT = (
    "To reset your VPN password, use the self-service portal and follow the two-factor verification "
    "steps to restore access within minutes."
)


def test_employee_is_blocked_from_restricted_topic(register, client):
    admin_headers = register(email="admin@secureco.example", organization="SecureCo")
    employee_headers = register(email="employee@secureco.example", organization="SecureCo")
    project_id = _create_project(client, admin_headers)

    _upload(client, admin_headers, project_id, "comp.txt", RESTRICTED_CONTENT, "Finance", "Restricted")
    _upload(client, admin_headers, project_id, "faq.txt", PUBLIC_CONTENT, "Support", "Public")

    response = client.post(
        f"/projects/{project_id}/knowledge/search",
        json={"query": "What is the executive salary range?"},
        headers=employee_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["restricted"] is True
    assert body["chunks"] == []
    assert "isn't authorized" in body["message"]


def test_admin_can_retrieve_restricted_topic(register, client):
    admin_headers = register(email="admin2@secureco2.example", organization="SecureCo2")
    project_id = _create_project(client, admin_headers)
    _upload(client, admin_headers, project_id, "comp.txt", RESTRICTED_CONTENT, "Finance", "Restricted")

    response = client.post(
        f"/projects/{project_id}/knowledge/search",
        json={"query": "What is the executive salary range?"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["restricted"] is False
    assert len(body["chunks"]) > 0
    assert body["chunks"][0]["classification"] == "Restricted"


def test_employee_can_retrieve_non_restricted_topic(register, client):
    admin_headers = register(email="admin3@secureco3.example", organization="SecureCo3")
    employee_headers = register(email="employee3@secureco3.example", organization="SecureCo3")
    project_id = _create_project(client, admin_headers)
    _upload(client, admin_headers, project_id, "faq.txt", PUBLIC_CONTENT, "Support", "Public")

    response = client.post(
        f"/projects/{project_id}/knowledge/search",
        json={"query": "How do I reset my VPN password?"},
        headers=employee_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["restricted"] is False
    assert len(body["chunks"]) > 0
    assert "VPN" in body["chunks"][0]["content"] or "vpn" in body["chunks"][0]["content"].lower()


def test_assistant_chat_mirrors_the_same_restriction(register, client):
    admin_headers = register(email="admin4@secureco4.example", organization="SecureCo4")
    employee_headers = register(email="employee4@secureco4.example", organization="SecureCo4")
    project_id = _create_project(client, admin_headers)
    _upload(client, admin_headers, project_id, "comp.txt", RESTRICTED_CONTENT, "Finance", "Restricted")

    response = client.post(
        f"/projects/{project_id}/assistants/chat",
        json={"message": "Tell me the executive salary range"},
        headers=employee_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["restricted"] is True
    assert body["generatedBy"] == "mock"
    assert body["sources"] == []


def test_assistant_chat_answers_normally_when_not_restricted(register, client):
    admin_headers = register(email="admin5@secureco5.example", organization="SecureCo5")
    project_id = _create_project(client, admin_headers)
    _upload(client, admin_headers, project_id, "faq.txt", PUBLIC_CONTENT, "Support", "Public")

    response = client.post(
        f"/projects/{project_id}/assistants/chat",
        json={"message": "How do I reset my VPN password?"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["restricted"] is False
    assert body["generatedBy"] == "mock"  # no ANTHROPIC_API_KEY configured in tests
    assert len(body["sources"]) > 0
    assert "faq.txt" in body["reply"]
