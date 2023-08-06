from fastapi import APIRouter, Response, status

from apiautomata.holder.ItemHolder import ItemHolder
from apiautomata.process.ProcessInvoker import ProcessInvoker

router = APIRouter()


@router.post('/process/invoke', status_code=200)
async def invoke_process(process_name: str, response: Response):
    process_run_command = ItemHolder.get('process-run-command')
    process_invoker = ProcessInvoker(process_run_command, process_name)
    result = process_invoker.invoke_process()
    response.status_code = status.HTTP_406_NOT_ACCEPTABLE if result.startswith('error:') else status.HTTP_201_CREATED
    return result
