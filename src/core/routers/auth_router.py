from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Path, HTTPException
import json
import websockets
import logging
from typing import Optional

from src.core.models.building import Building
from src.database import yield_db_session
from src.exceptions import BadRequest, NotFound
from src.responses import success
from src.logger import get_logger
from src.core.schemas.user_schema import BuildingInputField,BuildingUserInputField

logger = get_logger(__name__)

router = APIRouter()


@router.get('/building/list', description="List All Buildings")
async def list_buildings(
    db_session: AsyncSession = Depends(yield_db_session)
):
    buildings = await Building.list(db_session)
    return success([building.to_dict for building in buildings])

@router.post('/building/register', description="Register a New Building")
async def register_building(
    request: Request,
    body: BuildingInputField,
    db_session: AsyncSession = Depends(yield_db_session)
):
    the_user = await Building.filter_by(
        db_session,
        building_url=body.building_url
    )

    if the_user:
        logger.info(
            f"{body.building_url!r} is  registered in the system."
        )

        raise BadRequest(
            "Sorry, but the building is already registered in the system."
        )

    new_building = await Building.create(db_session, name=body.name, building_url=body.building_url, access_token=body.access_token)

    return new_building.to_dict

@router.put('/building/edit/{building_id}', description="Edit an Existing Building")
async def edit_building(
    request: Request,
    building_id: int = Path(..., description="The ID of the building to edit"),
    body: BuildingInputField = Depends(),
    db_session: AsyncSession = Depends(yield_db_session)
):
    building = await Building.get_by_id(db_session, building_id)
    
    if not building:
       raise HTTPException(status_code=404, detail="Building not found.")


    await building.update(
        db_session,
        name=body.name,
        building_url=body.building_url,
        access_token=body.access_token
    )
    
    return success(building.to_dict())

@router.delete('/building/delete/{building_id}', description="Delete a Building")
async def delete_building(
    building_id: int = Path(..., description="The ID of the building to delete"),
    db_session: AsyncSession = Depends(yield_db_session)
):
    success_flag = await Building.delete(db_session, building_id)
    if not success_flag:
        raise HTTPException(status_code=404, detail="Building not found.")
    return success({"message": "Building deleted successfully."})

class HomeAssistantWS:
    def __init__(self, url: str, access_token: str):
        self.url = url
        self.access_token = access_token
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.message_id = 1

    async def connect(self) -> None:
        try:
            print('------connecting----')
            self.websocket = await websockets.connect(self.url)
            print('----test--',self.websocket)
            auth_required = await self.websocket.recv()
            logger.info("Authentication required")
            auth_message = {"type": "auth", "access_token": 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0NzM5ZjE3MDNhNGQ0NDUxYjYwMWI2YTEyMzRmNThmYyIsImlhdCI6MTczOTgwMTU0MSwiZXhwIjoyMDU1MTYxNTQxfQ.H-mcQOdUgl5V7jaVEp_RJNIOgdelxZTGa3q2rDyH0Os'}
            await self.websocket.send(json.dumps(auth_message))
            auth_response = json.loads(await self.websocket.recv())
            if auth_response.get("type") == "auth_ok":
                logger.info("Authentication successful")
            else:
                raise Exception("Authentication failed")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            if self.websocket:
                await self.websocket.close()
            raise

    async def create_user(self, username: str, password: str, display_name: Optional[str] = None,
                          local_only: bool = False, administrator: bool = False) -> dict:
        if not self.websocket:
            raise Exception("Not connected")
        try:
            name = display_name if display_name else username
            group_ids = ["system-admin"] if administrator else ["system-users"]
            create_user_message = {"id": self.message_id, "type": "config/auth/create", "name": name, "group_ids": group_ids, "local_only": local_only}
            await self.websocket.send(json.dumps(create_user_message))
            user_response = await self.websocket.recv()
            logger.info("Create User Response: %s", user_response)
            user_data = json.loads(user_response)
            user_id = user_data.get("result", {}).get("user", {}).get("id")
            self.message_id += 1
            message = {"id": self.message_id, "type": "config/auth_provider/homeassistant/create", "user_id": user_id, "username": username, "password": password}
            self.message_id += 1
            await self.websocket.send(json.dumps(message))
            response = json.loads(await self.websocket.recv())
            if "error" in response:
                raise Exception(f"Error creating user: {response['error']}")
            return response
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def close(self) -> None:
        if self.websocket:
            await self.websocket.close()

@router.post("/building/create-user/{building_id}", description="Create User via WebSocket")
async def create_user_via_ws(
    building_id: int = Path(..., description="The ID of the building"),
    body: BuildingUserInputField = Depends(),
    db_session: AsyncSession = Depends(yield_db_session)
):
    print(building_id)
    building = await Building.get(db_session, building_id)
    print(building.building_url,building.access_token,'---------')
    if not building:
        raise HTTPException(status_code=404, detail="Building not found.")

    print(body)
    client = HomeAssistantWS(url="ws://home2.msh.srvmysmarthomes.us:8002/api/websocket", access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0NzM5ZjE3MDNhNGQ0NDUxYjYwMWI2YTEyMzRmNThmYyIsImlhdCI6MTczOTgwMTU0MSwiZXhwIjoyMDU1MTYxNTQxfQ.H-mcQOdUgl5V7jaVEp_RJNIOgdelxZTGa3q2rDyH0Os")
    
    try:
        await client.connect()
        response = await client.create_user(
            username=body.username,
            password=body.password,
            display_name=body.display_name,
            local_only=body.local_access_only if body.local_access_only is not None else False,
            administrator=body.administrator if body.administrator is not None else False
        )
        return success(response)
    except Exception as e:
        logger.error(f"Error in create_user_via_ws: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {e}")
    finally:
        await client.close()
        logger.info("WebSocket connection closed")