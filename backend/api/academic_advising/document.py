"""Document API

Document routes are used to retrieve document information from DB populated by Google Docs API."""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Sequence
from backend.models.academic_advising.document_section import DocumentSection
from backend.models.public_user import PublicUser
from backend.models.academic_advising.document_details import DocumentDetails

from ...services.academic_advising.document_services import DocumentService
from ...services.user import UserService
from ...services.exceptions import ResourceNotFoundException, UserPermissionException
from ...api.authentication import registered_user
from ...models.user import User

__authors__ = ["Emmalyn Foster"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


api = APIRouter(prefix="/api/documents")
openapi_tags = {
    "name": "Documents",
    "description": "Retrieve Documents"
}

@api.get("", tags=["Documents"])
def refresh_documents(
    document_service: DocumentService = Depends(),
) -> list[DocumentDetails]:
    """Refresh the documents in the database from Google Docs API"""
    return document_service.refresh_documents()

@api.get("/all", tags=["Documents"])
def get_all_documents(
    document_service: DocumentService = Depends(),
) -> list[DocumentDetails]:
    """Get a list of all documents in the database"""
    return document_service.all()

@api.get("/search/{query}", tags=["Documents"])
def search_documents(
    document_service: DocumentService = Depends(),
    query: str = "",
) -> list[DocumentSection]:
    """Return a list of document sections based on search query ordered by rank"""

    return document_service.search_document_sections(query)