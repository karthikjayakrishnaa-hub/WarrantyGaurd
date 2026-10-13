from fastapi import APIRouter, Depends
from fastapi.responses import EventSourceResponse
import asyncio
from app.tasks.task_store import in_memory_task_store

router = APIRouter()

@router.get("/{claim_id}/progress")
async def stream_pipeline_progress(claim_id: int):
    async def event_generator():
        while True:
            # Check in-memory store
            state = in_memory_task_store.get(claim_id)
            if state:
                yield {"data": str(state)}
                if state.get("status") in ["completed", "failed"]:
                    break
            else:
                yield {"data": "{'status': 'pending'}"}
            await asyncio.sleep(1)
            
    return EventSourceResponse(event_generator())