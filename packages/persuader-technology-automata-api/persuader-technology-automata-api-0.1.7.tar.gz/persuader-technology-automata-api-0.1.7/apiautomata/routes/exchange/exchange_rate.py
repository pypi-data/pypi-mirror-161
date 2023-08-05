from typing import Dict

from core.exchange.InstrumentExchange import InstrumentExchange
from exchangerepo.repository.ExchangeRateRepository import ExchangeRateRepository
from fastapi import APIRouter

from apiautomata.holder.ItemHolder import ItemHolder

router = APIRouter()


@router.get('/exchange/rate/{instrument_from}/{instrument_to}', response_model=Dict)
async def get_exchange_rate(instrument_from, instrument_to):
    instrument_exchange = InstrumentExchange(instrument_from, instrument_to)
    exchange_rate_repository = ItemHolder.get_entity(ExchangeRateRepository)
    instant_rate = exchange_rate_repository.retrieve_latest(instrument_exchange)
    if instant_rate is not None:
        return {'rate': str(instant_rate.rate), 'instant': instant_rate.instant}
    return {}
