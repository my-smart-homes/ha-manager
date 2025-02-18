from fastapi import APIRouter

from src.logger import get_logger
from src.responses import success

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", include_in_schema=False)
@router.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return success(data={"status": "OK"})
