import pytest
from src.app import create_app

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test',
        'WTF_CSRF_ENABLED': False
    })
    
    # Create the database and load test data
    with app.app_context():
        # The database tables are created in the create_app function
        pass
    
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Customer Survey App' in response.data

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
