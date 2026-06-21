import pytest
from app import create_app
from app.extensions import db

class TestConfig:
    TESTING=True; SECRET_KEY='test'; SQLALCHEMY_DATABASE_URI='sqlite://'; SQLALCHEMY_TRACK_MODIFICATIONS=False
    WTF_CSRF_ENABLED=False; RATELIMIT_STORAGE_URI='memory://'; RATELIMIT_ENABLED=False
@pytest.fixture()
def app():
    app=create_app(TestConfig)
    with app.app_context():
        db.drop_all();db.create_all();yield app;db.session.remove();db.drop_all()
@pytest.fixture()
def client(app):return app.test_client()
