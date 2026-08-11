import pytest


@pytest.mark.django_db
def test_health_reports_database_readiness(client):
    response = client.get('/api/health/')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'service': 'furniture-api',
    }


@pytest.mark.django_db
def test_health_only_accepts_get(client):
    response = client.post('/api/health/')

    assert response.status_code == 405
