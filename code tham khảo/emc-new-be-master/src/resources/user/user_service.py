import asyncio
import boto3
from pydantic import NonNegativeFloat
from urllib.parse import unquote
from fastapi import UploadFile, HTTPException
from typing import Optional
from dataclasses import asdict 

from src.infra.vda.vda_service import vdaService
from src.config.settings import settings
from src.core.user.data import UserCreateUpdate, UserGroup, VDAUserRole, ListQueryOptions
from src.utils.error.error import AppException
from src.utils.dictionary.del_none_field import del_none_field

from src.utils.error.error import AppException

client = boto3.client('cognito-idp')

class UserService():
    def getVDAIdFromUser(self, user):
        attributes = user.get('UserAttributes')
        for attribute in attributes:
            if attribute.get('Name') == settings.vda_id_attribute:
                return attribute.get('Value')

    async def getVDAUserFromUser(self, user_res):
        vda_user_id = self.getVDAIdFromUser(user_res)
        if not vda_user_id:
            raise AppException(name='No vda Id!')
        user = await vdaService.getUserDetail(vda_user_id)
        return user

    async def get_user_by_id(self, id):
        vda_user = await vdaService.getUserDetail(id)
        user_InDB = {}
        try:
            user_InDB = await self.get_user_indb(vda_user.get('email'))
        except Exception as e:
            print('[Get user in DB error !]', e)
            print('[Error user]', id, vda_user)
        return dict(vda_user, **user_InDB)

    async def get_user_indb(self, username):
        user_res = client.admin_get_user(
            UserPoolId=settings.user_pool_id,
            Username=username
        )
        return user_res

    async def sync_user_from_vda(self):
        company_detail = await vdaService.getCompanyDetail()
        users = company_detail['users']
        for u in users:
            email = u['email']
            res = await self.get_user_in_db_by_email(email)
            user_exist = bool(res)

            if not user_exist:
                role = u['role'] 
                await self.create_user_in_db(email, u['_id'], role)

    async def sync_delete_user_with_vda(self):
        company_detail = await vdaService.getCompanyDetail()
        users = company_detail['users']
        users_in_db = await self.get_all_user_in_db()

        for u in users_in_db:
            email = next((x for x in u['Attributes'] if x['Name'] == 'email'), None)
            if not email:
                continue
            vda_user = next((u for u in users if u['email'] == email['Value']), None)

            if not vda_user:
                await self.delete_user_in_db(u['Username'])

    async def reset_temporary_password(self, user: UserCreateUpdate, temp_password: Optional[str]):
        try:
            response = client.admin_create_user(
                UserPoolId=settings.user_pool_id,
                Username=user['email'],
                MessageAction='RESEND',
                TemporaryPassword=temp_password if temp_password else settings.temporary_password
            )
        except Exception as e:
            raise AppException(name='User already changed password')


    async def delete_user(self, id: str):
        vda_user = await vdaService.getUserDetail(id)
        if not vda_user:
            raise AppException(name='User does not exist')
        
        await vdaService.delete_user(id)
        user_in_db = await self.get_user_in_db_by_email(vda_user['email'])
        if not user_in_db:
            return 

        response = await self.delete_user_in_db(user_in_db['Username'])
        return response

    async def get_user_in_db_by_email(self, email: str):
        response = client.list_users(
            UserPoolId=settings.user_pool_id,
            Filter=f'email = "{email}"'
        )
        user = response.get("Users")[0] if response.get("Users") else None
        return user

    async def delete_user_in_db(self, username: str):
        response = client.admin_delete_user(
            UserPoolId=settings.user_pool_id,
            Username = username
        )
        return response


    async def update_user(self, id: str, data: UserCreateUpdate ,avatar: Optional[UploadFile] = None):
        data = del_none_field(data if type(data) is dict else asdict(data))

        updated = await vdaService.update_user(id, data, avatar)
 
        if data.get('newPassword'):
            user = await vdaService.getUserDetail(id)
            self.set_user_password(user['email'], data.get('newPassword'), True)

        return updated

    def set_user_password(self, username: str, password: str, permanent: Optional[bool]):
        command = client.admin_set_user_password(
            UserPoolId=settings.user_pool_id,
            Username=username,
            Password=password,
            Permanent=permanent
        )

        return command

    async def create_new_user(self, data: UserCreateUpdate, avatar: Optional[UploadFile] = None):
        data = data if type(data) is dict else asdict(data)
        create_data = {
            **data,
            "status": "active",
            "assign": ["drone", "commercial", "residential"]
        }
        vda_user = await vdaService.create_user(create_data, avatar)
        await self.create_user_in_db(data.get('email'), vda_user.get('_id'), data.get('role'), data.get('password'))

        return vda_user

    async def create_user_in_db(self, email: str, vda_id: Optional[str], role: Optional[VDAUserRole], tempPassword: Optional[str]):
        input = {
            "UserPoolId": settings.user_pool_id,
            "Username": email,
            "DesiredDeliveryMediums": ['EMAIL'],
            "TemporaryPassword": tempPassword or settings.temporary_password,
            "UserAttributes": [
                {'Name': 'email', 'Value': email},
                {'Name': 'email_verified', 'Value': 'true'}
            ]
        }
        if vda_id:
            input['UserAttributes'] = [
                {
                    "Name": settings.vda_id_attribute,
                    "Value": vda_id
                }
            ]
        client.admin_create_user(**input)
        client.admin_update_user_attributes(
            UserPoolId=settings.user_pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email_verified', 'Value': 'true'}
            ]
        )
        if role:
            group = self.vda_role_to_group(role)
            await self.add_user_to_group(email, group.value)

    def vda_role_to_group(self, role: VDAUserRole) :
        if role == VDAUserRole.Admin:
            return UserGroup.Admin
        elif role == VDAUserRole.SuperAdmin:
            return UserGroup.SuperAdmin
        else:
            return UserGroup.User

    async def add_user_to_group(self, email: str, group: UserGroup):
        response = client.admin_add_user_to_group(
            UserPoolId=settings.user_pool_id,
            Username=email,
            GroupName=group,
        )

    async def list_user_auth_events(self, options: ListQueryOptions):
        
        params = {
            "UserPoolId": settings.user_pool_id,
            'Username': options.email,
            'MaxResults': int( options.maxResults) if  options.maxResults else None
        }
        if options.nextToken:
            params['NextToken'] = unquote(options.nextToken)
    
        response = client.admin_list_user_auth_events(**params) if options.email and options.email != 'null' else None
        return response

    async def get_all_company_user(self):
        company = await vdaService.getCompanyDetail()
        user_ids = [user.get('_id') for user in company.get('users')]
        reqs = [vdaService.getUserDetail(user_id) for user_id in user_ids]
        users = await asyncio.gather(*reqs)
        return users

    async def get_all_user_in_db(self):
        response = client.list_users(
            UserPoolId=settings.user_pool_id
        )
        users = response['Users']
        return users

user_service = UserService()
