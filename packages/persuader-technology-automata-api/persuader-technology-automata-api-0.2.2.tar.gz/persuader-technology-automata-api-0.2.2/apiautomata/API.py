from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apiautomata.routes import home, proxy
from apiautomata.routes.exchange import instrument_exchange, exchange_rate
from apiautomata.routes.missing import missing
from apiautomata.routes.process import process_enablement, process_status, process_invoke
from apiautomata.routes.transform import exchange_transform, trade_transform

app = FastAPI()

app.include_router(home.router)
app.include_router(proxy.router)
app.include_router(missing.router)
app.include_router(instrument_exchange.router)
app.include_router(exchange_transform.router)
app.include_router(trade_transform.router)
app.include_router(exchange_rate.router)
app.include_router(process_enablement.router)
app.include_router(process_status.router)
app.include_router(process_invoke.router)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup_event():
    print('Starting...')


@app.on_event('shutdown')
async def shutdown_event():
    print('Stopping...')
