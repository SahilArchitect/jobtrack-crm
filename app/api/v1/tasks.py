from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.worker.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
def task_status(task_id: str, current_user: CurrentUser) -> dict[str, object]:
    task = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": task.status, "result": task.result if task.ready() else None}
