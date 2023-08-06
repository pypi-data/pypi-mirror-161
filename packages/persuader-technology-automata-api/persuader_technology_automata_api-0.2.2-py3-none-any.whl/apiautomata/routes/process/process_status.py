from fastapi import APIRouter
from processrepo.Process import Process
from processrepo.repository.ProcessRepository import ProcessRepository

from apiautomata.holder.ItemHolder import ItemHolder

router = APIRouter()


@router.get('/process/status/{market}/{name}', response_model=Process)
async def get_process_status(market, name):
    process_repository = ItemHolder.get_entity(ProcessRepository)
    return process_repository.retrieve(name, market)
