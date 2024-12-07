"""Webhook API

Webhook routes are used to receieve notifications from document and calendar webhooks and update the database accordingly."""

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
from ...services.academic_advising.webhook_notification_handler import WebhookService

__authors__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


api = APIRouter(prefix="/api/webhook")
openapi_tags = {
    "name": "Webhook",
    "description": "Receive Google Webhook notifications",
}


@api.put("/webhook", tags=["Webhook"])
def resubscribe():
    """Resubscribe to Google Calendar notifications"""
    # Set up the jobs to run the webhook service after 28 days
    return


@api.post("/webhook", tags=["Webhook"])
def handler(
    webhook_service: WebhookService = Depends(),
):
    """Handle incoming Google Webhook notifications"""
    return webhook_service.webhook_handler()
