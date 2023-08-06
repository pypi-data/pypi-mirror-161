from fastapi import APIRouter
from processrepo.ProcessRunProfile import ProcessRunProfile
from processrepo.repository.ProcessRunProfileRepository import ProcessRunProfileRepository

from apiautomata.holder.ItemHolder import ItemHolder

router = APIRouter()


@router.get('/process/{market}/{name}', response_model=ProcessRunProfile)
async def get_process_run_profile(market, name):
    process_run_profile_repository = ItemHolder.get_entity(ProcessRunProfileRepository)
    return process_run_profile_repository.retrieve(name, market)


@router.post('/process/{market}/{name}', response_model=bool)
async def enable_proces(market, name, enable: bool = True):
    process_run_profile_repository = ItemHolder.get_entity(ProcessRunProfileRepository)
    process_run_profile = process_run_profile_repository.retrieve(name, market)
    process_run_profile.enabled = enable
    process_run_profile_repository.store(process_run_profile)
    return process_run_profile.enabled
