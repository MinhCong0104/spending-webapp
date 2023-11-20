import unittest
from unittest.mock import patch
from mongoengine import connect, disconnect
from fastapi.testclient import TestClient
from app.domain.auth.entity import AuthInfo
from app.main import app
import mongomock
from app.infra.database.models.user import User as UserModel
from app.infra.security.security_service import get_password_hash


class TestGoogleAuthApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        disconnect()
        connect("mongoenginetest", host="mongodb://localhost:1234", mongo_client_class=mongomock.MongoClient)
        cls.client = TestClient(app)
        cls.user = UserModel(
            email="test@gmail.com",
            status="active",
            role="accountant",
            hashed_password=get_password_hash(password="local@local"),
        ).save()

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def test_google_token(self):
        with patch("app.use_cases.auth.google.GoogleAuthUseCase.fetch_user_info") as mock_access_token:
            mock_access_token.return_value = AuthInfo(
                **{
                    "iss": "https://accounts.google.com",
                    "azp": "667411231276-1s90svln4n5j1l04cnedgiilb6fgno72.apps.googleusercontent.com",
                    "aud": "667411231276-1s90svln4n5j1l04cnedgiilb6fgno72.apps.googleusercontent.com",
                    "sub": "102663488834299368719",
                    "email": "danhnv.bhsoft@gmail.com",
                    "email_verified": "true",
                    "nbf": "1698830792",
                    "name": "Danh Ngô Văn",
                    "picture": (
                        "https://lh3.googleusercontent.com/a/ACg8ocLLUwCrU53Rr8ZOka9pvt4bgu2QfGJOa99YF3YFKH00Zw=s96-c"
                    ),
                    "given_name": "Danh",
                    "family_name": "Ngô Văn",
                    "locale": "vi",
                    "iat": "1698831092",
                    "exp": "1698834692",
                    "jti": "77817cf2c18c1e5635dd11dac8760990bb523889",
                    "alg": "RS256",
                    "kid": "f5f4bf46e52b31d9b6249f7309ad0338400680cd",
                    "typ": "JWT",
                }
            )
            r = self.client.get("/api/v1/auth/google/token", params={"id_token": "xxxx"})
            print(r.text)
            assert r.status_code == 200
            assert r.json().get("access_token")
            user = UserModel.objects(email="danhnv.bhsoft@gmail.com").get()
            assert user.avatar
