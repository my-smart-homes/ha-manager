from typing import Dict, List, Optional, Union

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': 'true',
}


class RootResponseModel(BaseModel):
    success: bool


class ErrorModel(BaseModel):
    code: Union[str, int]
    field: Optional[str]
    message: str


class SucessResponseModel(RootResponseModel):
    data: Optional[Union[Dict, List]]
    success: bool = True


class ErrorResponseModel(RootResponseModel):
    errors: Union[List[ErrorModel], List]
    success: bool = False


def response(data, success, status_code: int, **kwargs):
    content = {}

    if success:
        content = SucessResponseModel(
            data=data,
            success=success
        )

    else:
        content = ErrorResponseModel(
            errors=data,
            success=success
        )

    return JSONResponse(
        content=jsonable_encoder(content, **kwargs),
        status_code=status_code,
        headers=headers
    )


def success(data, status_code=status.HTTP_200_OK, **kwargs):
    return response(
        data=data,
        success=True,
        status_code=status_code,
        **kwargs
    )


def error(data, status_code=status.HTTP_400_BAD_REQUEST):
    return response(
        data=data,
        success=False,
        status_code=status_code
    )
