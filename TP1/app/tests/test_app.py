from app import app

def test_add_route():
    client = app.test_client()
    response = client.get("/add/2/3")
    assert response.status_code == 200
    assert response.get_json()["result"] == 5

def test_home_route():
    client = app.test_client()
    response = client.get("/")
    data = response.get_json()
    assert "message" in data
