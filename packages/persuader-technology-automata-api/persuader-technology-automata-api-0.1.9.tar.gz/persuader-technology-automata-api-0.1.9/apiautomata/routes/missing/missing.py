from typing import List

from fastapi import APIRouter
from missingrepo.Missing import Missing
from missingrepo.repository.MissingRepository import MissingRepository

from apiautomata.holder.ItemHolder import ItemHolder

router = APIRouter()


@router.get('/missing', response_model=List[Missing])
async def get_all_missing():
    missing_repository = ItemHolder.get_entity(MissingRepository)
    return missing_repository.retrieve()


@router.delete('/missing')
async def delete_missing(missing: Missing):
    missing_repository = ItemHolder.get_entity(MissingRepository)
    missing_repository.delete(missing)
    return 'SUCCESS'
