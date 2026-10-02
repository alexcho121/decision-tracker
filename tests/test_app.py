from backend.app import create_app


def test_full_decision_flow(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(testing=True, database_url=f"sqlite:///{db_path}")
    client = app.test_client()

    health = client.get("/health")
    assert health.status_code == 200

    created = client.post("/api/decisions", json={"title": "Which laptop should I buy?"})
    assert created.status_code == 201
    decision_id = created.get_json()["id"]

    first = client.post(f"/api/decisions/{decision_id}/options", json={"title": "Laptop A"})
    second = client.post(f"/api/decisions/{decision_id}/options", json={"title": "Laptop B"})
    assert first.status_code == 201
    assert second.status_code == 201
    first_id = first.get_json()["id"]

    pro = client.post(f"/api/options/{first_id}/pros-cons", json={"type": "pro", "text": "Better battery"})
    con = client.post(f"/api/options/{first_id}/pros-cons", json={"type": "con", "text": "More expensive"})
    assert pro.status_code == 201
    assert con.status_code == 201

    selected = client.post(f"/api/decisions/{decision_id}/select", json={"option_id": first_id})
    assert selected.status_code == 200

    loaded = client.get(f"/api/decisions/{decision_id}")
    assert loaded.status_code == 200
    payload = loaded.get_json()
    assert len(payload["options"]) == 2
    chosen = next(option for option in payload["options"] if option["id"] == first_id)
    assert chosen["is_selected"] is True
    assert len(chosen["pros_and_cons"]) == 2


def test_validation(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(testing=True, database_url=f"sqlite:///{db_path}")
    client = app.test_client()

    assert client.post("/api/decisions", json={"title": ""}).status_code == 400
    assert client.post("/api/options/not-real/pros-cons", json={"type": "maybe", "text": "x"}).status_code == 400
