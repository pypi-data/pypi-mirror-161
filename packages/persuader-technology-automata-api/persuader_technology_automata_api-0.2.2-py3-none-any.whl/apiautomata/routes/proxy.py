import asyncio
from fastapi import APIRouter

from apiautomata.proxify.Proxify import Proxify

router = APIRouter()


@router.get('/proxy')
async def proxy(url: str = None):
    proxify = Proxify(url)

    tasks = []
    task = asyncio.create_task(Proxify.get_end_point_status(proxify))
    tasks.append(task)

    await asyncio.gather(*tasks)

    return proxify
