ANA = {"fullname": "Ana Lopez", "phone": "5551234", "email": "ana@example.com"}
LUIS = {"fullname": "Luis Perez", "phone": "5559876", "email": "luis@example.com"}


def add(client, data, follow=True):
    return client.post("/add_contact", data=data, follow_redirects=follow)


def test_index_empty(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Flask Contacts App" in resp.data


def test_add_contact(client, db_rows):
    resp = add(client, ANA)
    assert resp.status_code == 200
    assert b"Contact Added successfully" in resp.data
    assert b"ana@example.com" in resp.data
    assert db_rows()[0]["fullname"] == "Ana Lopez"


def test_add_duplicate_email_shows_error(client, db_rows):
    add(client, ANA)
    resp = add(client, {**LUIS, "email": ANA["email"]})
    assert b"already exists" in resp.data
    assert b"alert-danger" in resp.data
    assert len(db_rows()) == 1


def test_add_requires_email(client, db_rows):
    resp = add(client, {**ANA, "email": "  "})
    assert b"Email is required" in resp.data
    assert db_rows() == []


def test_edit_form_prefilled(client, db_rows):
    add(client, ANA)
    cid = db_rows()[0]["id"]
    resp = client.get(f"/edit/{cid}")
    assert resp.status_code == 200
    assert b'value="Ana Lopez"' in resp.data


def test_edit_missing_returns_404(client):
    assert client.get("/edit/999").status_code == 404


def test_update_contact(client, db_rows):
    add(client, ANA)
    cid = db_rows()[0]["id"]
    resp = client.post(f"/update/{cid}", data={**ANA, "fullname": "Ana Ruiz"},
                       follow_redirects=True)
    assert b"Contact Updated Successfully" in resp.data
    assert db_rows()[0]["fullname"] == "Ana Ruiz"


def test_update_duplicate_email_shows_error(client, db_rows):
    add(client, ANA)
    add(client, LUIS)
    luis_id = db_rows()[1]["id"]
    resp = client.post(f"/update/{luis_id}", data={**LUIS, "email": ANA["email"]},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert db_rows()[1]["email"] == LUIS["email"]


def test_update_missing_returns_404(client):
    assert client.post("/update/999", data=ANA).status_code == 404


def test_delete_contact(client, db_rows):
    add(client, ANA)
    cid = db_rows()[0]["id"]
    resp = client.post(f"/delete/{cid}", follow_redirects=True)
    assert b"Contact Removed Successfully" in resp.data
    assert db_rows() == []


def test_delete_via_get_not_allowed(client, db_rows):
    add(client, ANA)
    cid = db_rows()[0]["id"]
    assert client.get(f"/delete/{cid}").status_code == 405
    assert len(db_rows()) == 1


def test_delete_rejects_sql_injection(client, db_rows):
    add(client, ANA)
    add(client, LUIS)
    assert client.post("/delete/1%20OR%201=1").status_code == 404
    assert len(db_rows()) == 2


def test_csrf_required_when_enabled(flask_app, client, db_rows):
    flask_app.config["WTF_CSRF_ENABLED"] = True
    try:
        assert client.post("/add_contact", data=ANA).status_code == 400
        assert db_rows() == []
    finally:
        flask_app.config["WTF_CSRF_ENABLED"] = False
