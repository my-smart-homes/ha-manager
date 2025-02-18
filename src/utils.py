from fastapi import Request
import logging
from src.config import settings
logger = logging.getLogger('custom')


def get_tenant_name(request: Request) -> str:

    hostname = request.headers.get("host", "")
    tenant = hostname.split(".")[0]

    return tenant
