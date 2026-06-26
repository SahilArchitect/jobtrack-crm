def test_register_login_and_me(client):
    payload = {
        "tenant_name": "Solo Hunt",
        "email": "sahil@example.com",
        "full_name": "Sahil Bhatti",
        "password": "Password123!",
    }
    register = client.post("/api/v1/auth/register", json=payload)
    assert register.status_code == 201
    assert register.json()["role"] == "admin"

    login = client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_company_job_application_analytics_and_csv(client, auth_headers):
    company = client.post(
        "/api/v1/companies",
        headers=auth_headers,
        json={"name": "Qualcomm", "location": "Hyderabad", "industry": "Semiconductors"},
    )
    assert company.status_code == 201, company.text
    company_id = company.json()["id"]

    job = client.post(
        "/api/v1/job-postings",
        headers=auth_headers,
        json={
            "company_id": company_id,
            "role_title": "Automation Engineer",
            "external_job_id": "3091673",
            "location": "Bangalore",
            "status": "open",
        },
    )
    assert job.status_code == 201, job.text
    job_id = job.json()["id"]

    application = client.post(
        "/api/v1/applications",
        headers=auth_headers,
        json={
            "company_id": company_id,
            "job_posting_id": job_id,
            "resume_version": "R2-System-Test",
            "status": "applied",
            "priority": "urgent",
            "source": "referral",
        },
    )
    assert application.status_code == 201, application.text
    application_id = application.json()["id"]

    patch = client.patch(
        f"/api/v1/applications/{application_id}",
        headers=auth_headers,
        json={"status": "interview"},
    )
    assert patch.status_code == 200
    assert patch.json()["status"] == "interview"

    audit = client.get("/api/v1/audit-logs?entity_type=application", headers=auth_headers)
    assert audit.status_code == 200
    assert audit.json()["total"] >= 2

    analytics = client.get("/api/v1/analytics/summary", headers=auth_headers)
    assert analytics.status_code == 200
    assert analytics.json()["applications_by_status"]["interview"] == 1

    csv_export = client.get("/api/v1/applications/export/csv", headers=auth_headers)
    assert csv_export.status_code == 200
    assert "Qualcomm" in csv_export.text
    assert "Automation Engineer" in csv_export.text


def test_multi_tenant_isolation(client, auth_headers):
    first = client.post(
        "/api/v1/companies",
        headers=auth_headers,
        json={"name": "Private Company", "location": "Pune"},
    )
    assert first.status_code == 201

    second_register = client.post(
        "/api/v1/auth/register",
        json={
            "tenant_name": "Second Tenant",
            "email": "other@example.com",
            "full_name": "Other Admin",
            "password": "Password123!",
        },
    )
    assert second_register.status_code == 201
    second_login = client.post(
        "/api/v1/auth/login",
        data={"username": "other@example.com", "password": "Password123!"},
    )
    second_token = second_login.json()["access_token"]
    second_headers = {"Authorization": f"Bearer {second_token}"}

    list_response = client.get("/api/v1/companies", headers=second_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0
