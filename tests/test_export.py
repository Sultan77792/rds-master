import pytest
from app.utils.export import DataExporter
import os

def test_export_to_excel(client):
    # Login as admin
    client.post('/auth/login', json={
        'username': 'admin',
        'password': 'password'
    })
    
    # Test export route
    response = client.get('/fires/export')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'