
class TestCache:

    def test_get_cache_summary(self, client, mock_jwt_required):
        response = client.get('/cache')
        assert response.status_code == 200
        assert response.json == {
            'currsize': 0,
            'hits': 0,
            'maxsize': 50,
            'misses': 0
        }

    def test_get_cache_keys(self, client, mock_jwt_required):
        response = client.get('/cache/keys')
        assert response.status_code == 200
        assert response.json == []

    def test_clear_from_cache(self, client, mock_jwt_required):
        response = client.delete('/cache')
        assert response.status_code == 200
        assert response.json == {
            'message': 'File cache cleared',
            'success': True
        }

        response = client.delete("/cache", query_string={'id': 'abc123'})
        assert response.status_code == 200
        assert response.json == {
            'message': 'File not in cache',
            'success': False
        }
