"""Drop In API

Drop In routes are used to retrieve drop-ins from DB populated by Google Calendar API."""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Sequence
from backend.models.academic_advising.drop_in import DropIn
from backend.models.public_user import PublicUser
from backend.models.pagination import (
    DropInPaginationParams,
    Paginated,
    PaginationParams,
)

from ...services.academic_advising.drop_in import DropInService
from ...services.user import UserService
from ...services.exceptions import ResourceNotFoundException, UserPermissionException
from ...api.authentication import registered_user
from ...models.user import User

__authors__ = ["Emmalyn Foster"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


api = APIRouter(prefix="/api/drop-ins")
openapi_tags = {
    "name": "Drop-in Sessions",
    "description": "Retrieve CS Advising Drop-in Sessions.",
}


@api.get("/paginate", tags=["Drop-in Sessions"])
def list_drop_ins(
    subject: User = Depends(registered_user),
    drop_in_service: DropInService = Depends(),
    order_by: str = "",
    ascending: str = "true",
    filter: str = "",
    range_start: str = "",
    range_end: str = "",
) -> Paginated[DropIn]:
    """List drop-ins in time range via standard backend pagination query parameters."""

    pagination_params = DropInPaginationParams(
        order_by=order_by,
        ascending=ascending,
        filter=filter,
        range_start=range_start,
        range_end=range_end,
    )
    return drop_in_service.get_paginated_drop_ins(pagination_params, subject)


#@api.get("/all", tags=["Drop-ins", "all"])
#def get_all_drop_ins(drop_in_service: DropInService = Depends()) -> list[DropIn]:
#    """List all drop-ins"""
#    return drop_in_service.all()

@api.get(
    "/{id}",
    responses={404: {"model": None}},
    tags=["Drop-in Sessions"],
) 
def get_drop_in_by_id(
     id: int,
     drop_in_service: DropInService = Depends(),
) -> DropIn:
    """
    Get drop-in with matching id

    Args:
        id: an int representing a unique DropIn ID
        drop_in_service: a valid DropInService

    Returns:
        DropIn: a valid DropIn model corresponding to the given event id
    """
    return drop_in_service.get_by_id(id)