import motor.motor_asyncio
import urllib.parse
from src.config.settings import settings
from src.infra.secret.secret_service import secret_service

db_secret_name = settings.db_credential_secret_name

if db_secret_name:
    db_cf = secret_service.get_secret(db_secret_name)
    db_host = db_cf['DB_HOST']
    # db_port = db_cf['CONNECT_DB_PORT']
    username = db_cf['DB_USERNAME']
    password = db_cf['DB_PASSWORD']
    database_name = db_cf['DB_NAME']
    uri = f"mongodb+srv://{username}:{password}@{db_host}/?retryWrites=true&w=majority"
else:
    db_host = settings.db_host
    db_port = settings.connect_db_port
    username = urllib.parse.quote_plus(settings.mongodb_username)
    password = urllib.parse.quote_plus(settings.mongodb_password)
    database_name = settings.db_name
    uri = f"mongodb://{username}:{password}@{db_host}:{db_port}"

mission_images_collection = 'mission_images'
mission_score_collection = 'mission_scores'
version_polygon = 'mission_version'
mission_version_assign = "mission_version_assign"
mission_raw_image_favourite = "mission_raw_image_favourite"
mission_share = "mission_share"
mission_update_score_status = "mission_update_score_status"

_client = None
_db = None

def connect_db():
    global _client
    _client = motor.motor_asyncio.AsyncIOMotorClient(
        uri
        # authSource=database_name
    )
    global _db
    _db = _client[database_name]
    print('>>> db connected:', database_name)
    return _client


def close_db():
    _client.close()


def get_mission_images_collection():
    return _db[mission_images_collection]


def get_mission_score_collection():
    return _db[mission_score_collection]


def get_version_polygon_collection():
    return _db[version_polygon]


def get_mission_version_assign_collection():
    return _db[mission_version_assign]


def get_mission_raw_image_favourite():
    return _db[mission_raw_image_favourite]


def get_mission_share():
    return _db[mission_share]

def get_mission_update_score_status():
    return _db[mission_update_score_status]