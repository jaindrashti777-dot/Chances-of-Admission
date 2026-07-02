def test_model_info(client):
    response = client.get("/api/v1/prediction/info")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_predict_validation_error(client):
    # Missing required fields like 'user_rank'
    payload = {
        "college_name": "NIT",
        "branch_name": "CSE"
    }
    response = client.post("/api/v1/prediction/", json=payload)
    assert response.status_code == 422 # Validation Error
    
def test_predict_model_unavailable(client, monkeypatch):
    from backend.app.inference.model_service import model_manager
    # Force model to be None to test graceful degradation
    monkeypatch.setattr(model_manager, "_model", None)
    
    payload = {
        "user_rank": 5000,
        "college_name": "NIT Trichy",
        "branch_name": "Computer Science",
        "institute_type": "NIT",
        "category": "OPEN",
        "quota": "OS",
        "seat_pool": "Gender-Neutral",
        "counselling_body": "JoSAA",
        "year": 2024,
        "round_number": 6
    }
    response = client.post("/api/v1/prediction/", json=payload)
    assert response.status_code == 503 # Service Unavailable (Model not loaded)
