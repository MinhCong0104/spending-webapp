import asyncio, json
from src.infra.secret.secret_service import secret_service
from src.infra.vda.vda_service import vdaService
from src.config.settings import settings
from src.resources.user.user_service import user_service
import datetime
from dateutil.relativedelta import relativedelta
from src.resources.missions import mission_service
from src.core.user.data import VDAUserRole


async def get_initialize_keys():
    google_map_secret = secret_service.get_secret(settings.google_maps_secret_name)
    return {
        'key': google_map_secret.get('Key')
    }


async def get_initialize_company_detail():
    company = await vdaService.getCompanyDetail()
    company_users = company.get('users')
    tasks = []
    for company_user in company_users:
        async def update_user_task(user):
            company_user = user
            user = await user_service.get_user_by_id(company_user.get('_id'))
            if not user:
                company_users.remove(company_user)
            company_user.update(user)
        tasks.append(update_user_task(company_user))
    await asyncio.gather(*tasks)
    return company


async def get_initialize_missions(user):
    date_now = datetime.datetime.now()
    date_from = date_now - relativedelta(years=5)
    missions = await vdaService.get_missions(date_from, date_now)
    version_reqs = []
    for curr in missions:
        for idx, v in enumerate(curr.get('versions')):
            async def get_data(mission, version, version_idx: int):
                data = await vdaService.get_mission_detail(version.get('_id'))
                if not data:
                    return
                # assign index for version
                version['index'] = version_idx
                # get newly assigned users to this version only
                mission_version_assigned_users = await mission_service.get_version_assign_users(version.get('_id'), False)

                # only admin, version creator and assigned user can see version
                user_allowed_version = user.get('role') in [VDAUserRole.Admin,
                                                     VDAUserRole.SuperAdmin] or (data.get('pilot') and user.get('_id') == data.get('pilot').get('_id')) or any(
                    u.get('_id') == user.get('_id') for u in mission_version_assigned_users)
                if user_allowed_version:
                    # mutate version in mission to include detailed data
                    mission.get('versions')[version_idx] = {
                        **version,
                        **data,
                    }

            version_reqs.append(get_data(curr, v, idx))
    await asyncio.gather(*version_reqs)

    # filter out mission version which doesn't get user allowed
    for m in missions:
        m['versions'] = [v for v in m.get('versions') if v.get('missionname')]

    # filter out mission with no versions
    return [m for m in missions if m.get('versions')]