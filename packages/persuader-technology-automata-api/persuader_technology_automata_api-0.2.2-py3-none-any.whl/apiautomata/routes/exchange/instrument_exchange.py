from typing import List

from core.exchange.InstrumentExchange import InstrumentExchange
from exchangerepo.repository.InstrumentExchangeRepository import InstrumentExchangeRepository
from fastapi import APIRouter

from apiautomata.holder.ItemHolder import ItemHolder

router = APIRouter()


@router.get('/exchange/instrument', response_model=List[InstrumentExchange])
async def get_all_exchange_instruments():
    instrument_exchange_repository = ItemHolder.get_entity(InstrumentExchangeRepository)
    holder = instrument_exchange_repository.retrieve()
    return holder.get_all()


@router.put('/exchange/instrument')
async def create_exchange_instrument(instrument_exchange: InstrumentExchange):
    instrument_exchange_repository = ItemHolder.get_entity(InstrumentExchangeRepository)
    instrument_exchange_repository.create(instrument_exchange)
    return instrument_exchange


@router.post('/exchange/instrument')
async def update_exchange_instrument(instrument_exchange: InstrumentExchange):
    instrument_exchange_repository = ItemHolder.get_entity(InstrumentExchangeRepository)
    instrument_exchange_repository.update(instrument_exchange)
    return instrument_exchange


@router.delete('/exchange/instrument')
async def delete_exchange_instrument(instrument_exchange: InstrumentExchange):
    instrument_exchange_repository = ItemHolder.get_entity(InstrumentExchangeRepository)
    instrument_exchange_repository.delete(instrument_exchange)
    return instrument_exchange
