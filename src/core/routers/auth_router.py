from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request, Path, HTTPException
from src.core.ha_websocket.main import HomeAssistantWS
from src.core.models.building import Building
from src.database import yield_db_session
from src.exceptions import BadRequest, NotFound
from src.responses import success
from src.logger import get_logger
from src.core.schemas.user_schema import BuildingInputField,BuildingUserInputField,BuildingUserUpdateField

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
    building = await Building.get(db_session, building_id)
    
    if not building:
       raise HTTPException(status_code=404, detail="Building not found.")


    await building.update(
        db_session,
        id=building_id,
        name=body.name,
        building_url=body.building_url,
        access_token=body.access_token
    )
    
    return success(building.to_dict)

@router.delete('/building/delete/{building_id}', description="Delete a Building")
async def delete_building(
    building_id: int = Path(..., description="The ID of the building to delete"),
    db_session: AsyncSession = Depends(yield_db_session)
):
    success_flag = await Building.delete(db_session, building_id)
    if not success_flag:
        raise HTTPException(status_code=404, detail="Building not found.")
    return success({"message": "Building deleted successfully."})

@router.post("/building/create-user/{building_id}", description="Create User via WebSocket")
async def create_user_via_ws(
    body: BuildingUserInputField,  # No default, this is fine here
    building_id: int = Path(..., description="The ID of the building"),
    db_session: AsyncSession = Depends(yield_db_session)
):

    print(building_id)
    building = await Building.get(db_session, building_id)
    print(building.building_url,building.access_token,'---------')
    if not building:
        raise HTTPException(status_code=404, detail="Building not found.")

    print(body)
    client = HomeAssistantWS(domain=building.building_url, access_token=building.access_token)
    
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
@router.put("/building/edit-user/{building_id}", description="Edit User via WebSocket")
async def edit_user_via_ws(
    body: BuildingUserUpdateField,
    building_id: int = Path(..., description="The ID of the building"),
    db_session: AsyncSession = Depends(yield_db_session)
):
    building = await Building.get(db_session, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found.")
    client = HomeAssistantWS(domain=building.building_url, access_token=building.access_token)
    try:
        await client.connect()
        response = await client.update_person(
            display_name=body.display_name,
            local_only=body.local_access_only if body.local_access_only is not None else False,
            user_id=body.user_id,
            group_ids=body.group_ids
        )
        return success(response)
    except Exception as e:
        logger.error(f"Error in edit_user_via_ws: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to edit user: {e}")
    finally:
        await client.close()
        logger.info("WebSocket connection closed")
@router.delete("/building/delete-user/{building_id}/{user_id}", description="Delete User via WebSocket")
async def delete_user_via_ws(
    building_id: int = Path(..., description="The ID of the building"),
    user_id: str = Path(..., description="The ID of the user to delete"),
    db_session: AsyncSession = Depends(yield_db_session)
):
    building = await Building.get(db_session, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found.")
    client = HomeAssistantWS(domain=building.building_url, access_token=building.access_token)
    try:
        await client.connect()
        response = await client.delete_person(user_id)
        return success(response)
    except Exception as e:
        logger.error(f"Error in delete_user_via_ws: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {e}")
    finally:
        await client.close()
        logger.info("WebSocket connection closed")
@router.get("/building/users", description="List all users from each building")
async def list_building_users(db_session: AsyncSession = Depends(yield_db_session)):
    buildings = await Building.list(db_session)
    results = {}

    for building in buildings:
        client = HomeAssistantWS(
            domain=building.building_url,
            access_token=building.access_token
        )
        try:
            await client.connect()
            # Send the person/list command and await the response.
            response = await client.list_persons()
            # Use the building name as the top-level key.
            response['building_id'] = building.id
            results[building.name] = response
        except Exception as e:
            logger.error(f"Error retrieving users from building {building.name}: {e}")
            results[building.name] = {"error": str(e)}
        finally:
            await client.close()

    return success(results)
