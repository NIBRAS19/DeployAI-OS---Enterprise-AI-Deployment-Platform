from app.models.enums import WorkflowStatus
from app.models.workflow import Workflow


def _create_project(client, headers):
    response = client.post(
        "/projects",
        json={"name": "Workflow Project", "customerName": "Cust", "environment": "development"},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_run_workflow_creates_a_run_and_activates_draft(register, client, db_session):
    headers = register(organization="WorkflowOrg")
    project_id = _create_project(client, headers)

    workflow = Workflow(
        id="wf-test-1", project_id=project_id, name="Test Workflow", status=WorkflowStatus.draft, success_rate=100.0
    )
    db_session.add(workflow)
    db_session.commit()

    response = client.post(f"/projects/{project_id}/workflows/{workflow.id}/run", headers=headers)
    assert response.status_code == 201
    run = response.json()
    assert run["outcome"] in ("success", "failed")
    assert run["detail"]

    updated = client.get(f"/projects/{project_id}/workflows", headers=headers).json()
    updated_workflow = next(w for w in updated if w["id"] == "wf-test-1")
    assert updated_workflow["status"] == "active"
    assert updated_workflow["lastRun"] is not None

    runs = client.get(f"/projects/{project_id}/workflows/{workflow.id}/runs", headers=headers).json()
    assert len(runs) == 1


def test_run_nonexistent_workflow_404s(register, client):
    headers = register(organization="WorkflowOrg2")
    project_id = _create_project(client, headers)
    response = client.post(f"/projects/{project_id}/workflows/does-not-exist/run", headers=headers)
    assert response.status_code == 404
