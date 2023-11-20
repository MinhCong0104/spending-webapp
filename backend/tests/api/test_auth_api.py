import unittest
from mongoengine import connect, disconnect
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
import mongomock
from app.infra.database.models.user import User as UserModel
from app.infra.security.security_service import get_password_hash, TokenData


class TestAuthApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        disconnect()
        connect("mongoenginetest", host="mongodb://localhost:1234", mongo_client_class=mongomock.MongoClient)
        cls.client = TestClient(app)
        cls.user = UserModel(
            email="local@local.com",
            status="active",
            role="accountant",
            hashed_password=get_password_hash(password="local@local"),
        ).save()

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_user_login(self):
        r = self.client.post("/api/v1/auth/login", data={"username": "local@local.com", "password": "local@local"})
        assert r.status_code == 200
        print(r.json())
        assert r.json().get("token").get("access_token")

    def test_user_logout(self):
        with patch("app.infra.security.security_service.verify_token") as mock_token:
            mock_token.return_value = TokenData(email=self.user.email)
            r = self.client.post(
                "/api/v1/auth/logout",
                headers={
                    "Authorization": "Bearer {}".format("xxx"),
                },
            )
            assert r.status_code == 200
