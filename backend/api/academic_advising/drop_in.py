"""Drop In API

Drop In routes are used to retrieve drop-ins from DB populated by Google Calendar API."""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Sequence
from backend.models.public_user import PublicUser
from backend.models.pagination import EventPaginationParams, Paginated, PaginationParams

from ...services.academic_advising.drop_in import DropInService
from ...services.user import UserService
from ...services.exceptions import ResourceNotFoundException, UserPermissionException
from ...api.authentication import registered_user
from ...models.user import User
