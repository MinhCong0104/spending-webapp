import json
import tempfile
from enum import Enum
from datetime import date
from io import BytesIO
import cv2 as cv
import numpy as np
import httpx
from typing import Optional
from fastapi import HTTPException, UploadFile
from src.config.settings import settings
from src.infra.secret.secret_service import secret_service
from src.core.user.data import UserCreateUpdate
from src.infra.http.http import get_response_json

class MissionDataFileType(str, Enum):
    demjpg = 'demjpg'
    demtif = 'demtif'
    demtile = 'demtile'
    hdobj = 'hdobj'
    geoobj = 'geoobj'
    tile3d = 'tile3d'
    orthojpg = 'orthojpg'
    orthotif = 'orthotif'
    orthotile = 'orthotile'


class VDAClientAuth(httpx.Auth):
    def __init__(self, VDA_API_URL, COMPANY_KEY, COMPANY_SECRET):
        self.VDA_API_URL = VDA_API_URL
        self.COMPANY_KEY = COMPANY_KEY
        self.COMPANY_SECRET = COMPANY_SECRET
        self.token = None

    def sync_auth_flow(self, request):
        raise RuntimeError("Cannot use a async authentication class with httpx.Client")
    
    async def async_auth_flow(self, request):
        token = await self.async_get_token() if not self.token else self.token
        request.headers["Authorization"] = f"Bearer {token}"
        response = yield request
        if response.status_code == 401:
          # If the server issues a 401 response then resend the request
          await self.async_get_token()
          request.headers['Authorization'] = self.token
          yield request

    async def async_get_token(self):
        async with httpx.AsyncClient(base_url=self.VDA_API_URL, timeout=settings.http_client_time_out) as client:
            res = await client.post('auth', data={'key': self.COMPANY_KEY, 'secret': self.COMPANY_SECRET})
        token = get_response_json(res)['token']
        self.token = token
        return token


class VDAService():
    def __init__(self):
        VDA_API_URL, COMPANY_KEY, COMPANY_SECRET = self.secret_data()
        self.VDA_API_URL = VDA_API_URL
        self.COMPANY_KEY = COMPANY_KEY
        self.COMPANY_SECRET = COMPANY_SECRET

        self.http_client = httpx.AsyncClient(
            base_url=self.VDA_API_URL,
            auth=VDAClientAuth(VDA_API_URL, COMPANY_KEY, COMPANY_SECRET),
            timeout=settings.http_client_time_out,
        )

    def secret_data(self):
        secret_data = secret_service.get_secret(settings.vda_api_secret_name)
        VDA_API_URL = secret_data.get('VDA_API_URL')
        COMPANY_KEY = secret_data.get('VDA_API_KEY')
        COMPANY_SECRET = secret_data.get('VDA_API_PASSWORD')
        return VDA_API_URL, COMPANY_KEY, COMPANY_SECRET

    async def delete_user(self, id: str):
        url = 'userdetail/%s' %id
        response = await self.http_client.delete(url)
        return response
    
    async def update_user(self, id: str, data: UserCreateUpdate, avatar: Optional[UploadFile] = None):
        url = 'userdetail/%s' %id
        if avatar:
            response = await self.http_client.put(url, data=data, files={'avatar': (avatar.filename, avatar.file, avatar.content_type)})
        else:
            response = await self.http_client.put(url, data=data)
                
        return get_response_json(response)

    async def create_user(self, data: UserCreateUpdate, avatar: Optional[UploadFile] = None):
        url = 'userdetail'

        if avatar:
            response = await self.http_client.post(url, data=data, files={'avatar': (avatar.filename, avatar.file, avatar.content_type)})
        else:
            response = await self.http_client.post(url, data=data)

        return get_response_json(response)

    async def getUserDetail(self, vdaUserId):
        url = 'userdetail/%s' % vdaUserId
        res = await self.http_client.get(url)

        return get_response_json(res)

    async def getCompanyDetail(self):
        url = 'companydetail'
        res = await self.http_client.get(url)

        return get_response_json(res)

    # -----------------MISSION----------------------#
    async def get_missions(self, from_date: date, to_date: date):
        url = 'missions'
        params = {
            'from': from_date,
            'to': to_date,
        }
        res = await self.http_client.get(url, params=params)

        return get_response_json(res)

    async def get_mission_detail(self, id):
        url = 'missions/%s/missiondata' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_demjpg(self, id):
        url = 'missions/%s/demjpg' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_demtif(self, id):
        url = 'missions/%s/demtif' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_demtile(self, id):
        url = 'missions/%s/demtile' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_hdobj(self, id):
        url = 'missions/%s/hdobj' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_geoobj(self, id):
        url = 'missions/%s/geoobj' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_title3d(self, id):
        url = 'missions/%s/title3d' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_orthojpg(self, id):
        url = 'missions/%s/orthojpg' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_orthotif(self, id):
        url = 'missions/%s/orthotif' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_orthotile(self, id):
        url = 'missions/%s/orthotile' % id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def update_company_detail(self, data: dict, logo: UploadFile):
        url = 'companydetail'
        if logo:
            res = await self.http_client.put(url, data=data, files={'logo': (logo.filename, logo.file, logo.content_type)})
        else:
            res = await self.http_client.put(url, data=data)
        return get_response_json(res)

    async def get_mission_raw_images(self, version_id: str):
        url = 'missions/%s/rawimages' % version_id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_image_annotation(self, image_id: str):
        url = 'userannotations/rawimage/%s' % image_id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def get_mission_image_annotation(self, image_id: str):
        url = "userannotations/rawimage/%s" % image_id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def create_mission_image_annotation(self, image_id: str, data: dict):
        url = "userannotations/rawimage/%s" % image_id
        res = await self.http_client.post(url, json=data)
        return get_response_json(res)

    async def update_mission_image_annotation(self, annotation_id: str, data: dict):
        url = "userannotations/rawimage/%s" % annotation_id
        res = await self.http_client.put(url, data=data)
        return get_response_json(res)

    async def delete_mission_image_annotation(self, annotation_id: str):
        url = "userannotations/rawimage/%s" % annotation_id
        res = await self.http_client.delete(url)

    async def get_mission_titleset_annotation(self, version_id: str):
        url = "userannotations/tileset/%s" % version_id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def create_titleset_annotation(self, mission_id: str, data: dict):
        url = "userannotations/tileset/%s" % mission_id
        res = await self.http_client.post(url, json=data)
        return get_response_json(res)

    async def update_titleset_annotation(self, annotation_id: str, data: dict):
        url = "userannotations/tileset/%s" % annotation_id
        res = await self.http_client.put(url, data=data)
        return get_response_json(res)

    async def delete_titleset_annotation(self, annotation_id: str):
        url = "userannotations/tileset/%s" % annotation_id
        res = await self.http_client.delete(url)

    async def get_mission_image_polygon(self, image_id: str):
        url = "userpolygons/rawimage/%s" % image_id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def create_mission_image_polygon(self, polygon_id: str, data: dict):
        url = "userpolygons/rawimage/%s" % polygon_id
        res = await self.http_client.post(url, json=data)
        return get_response_json(res)

    async def update_mission_image_polygon(self, polygon_id: str, data: dict):
        url = "userpolygons/rawimage/%s" % polygon_id
        res = await self.http_client.put(url, data=data)
        return get_response_json(res)

    async def delete_mission_image_polygon(self, polygon_id: str):
        url = "userpolygons/rawimage/%s" % polygon_id
        res = await self.http_client.delete(url)

    async def get_mission_titleset_polygon(self, mission_id: str):
        url = "userpolygons/tileset/%s" % mission_id
        res = await self.http_client.get(url)
        return get_response_json(res)

    async def create_mission_titleset_polygon(self, mission_id: str, data: dict):
        url = "userpolygons/tileset/%s" % mission_id
        res = await self.http_client.post(url, json=data)
        return get_response_json(res)

    async def update_mission_titleset_polygon(self, polygon_id: str, data: dict):
        url = "userpolygons/tileset/%s" % polygon_id
        res = await self.http_client.put(url, data=data)
        return get_response_json(res)

    async def delete_mission_titleset_polygon(self, polygon_id: str):
        url = "userpolygons/tileset/%s" % polygon_id
        res = await self.http_client.delete(url)

    async def get_resize_image(self, s3: str, key: str, size: int):
        api_url = 'presign/public'
        s3_url = f"https://{s3}.s3.amazonaws.com/{key}"
        res = await self.http_client.get(api_url, params={'url': s3_url})
        f = tempfile.SpooledTemporaryFile()
        f.write(res.content)
        f.seek(0)
        file_bytes = np.fromfile(f, np.uint8)
        img = cv.imdecode(file_bytes, cv.IMREAD_UNCHANGED)
        h, w, c = img.shape
        width = int(w/size) if size > 1 else w
        img_resize = self.image_resize(img, width)
        img_encode = cv.imencode('.jpg', img_resize)[1]
        io_buf = BytesIO(img_encode)
        return io_buf

    async def get_presign(self, url: str):
        api_url = 'presign/public'
        res = await self.http_client.get(api_url, params={'url': url})
        f = tempfile.SpooledTemporaryFile()
        f.write(res.content)
        f.seek(0)
        return f

    def image_resize(self, image, width=None, height=None, inter=cv.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

            resized = cv.resize(image, dim, interpolation=inter)

            return resized


vdaService = VDAService()

