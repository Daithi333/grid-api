
class TestApp:

    def test_app(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_invalid_requests(self, client):
        response = client.get("/invalid")
        assert response.status_code == 404
        assert response.json == {
            "message": "Requested route does not exist"
        }

        response = client.post("/")
        assert response.status_code == 405

        response = client.get("/files")
        assert response.status_code == 401
        assert response.json == {
            "msg": "Missing Authorization Header"
        }
