"""Webhook API

Webhook routes are used to receieve notifications from document and calendar webhooks and update the database accordingly."""

from fastapi import APIRouter, Depends, HTTPException, Request
from ...services.academic_advising.webhook_services import WebhookService

__authors__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


api = APIRouter(prefix="/api/webhook")
openapi_tags = {
    "name": "Webhook",
    "description": "Receive Google Webhook notifications",
}


@api.post("/resubscribe", tags=["Webhook"])
def resubscribe(
    webhook_service: WebhookService = Depends(),
):
    """Resubscribe to Google Calendar notifications"""
    return webhook_service.subscribe_to_document_and_calendar_changes()


@api.post("/webhook", tags=["Webhook"])
def handler(
    request: Request,
    webhook_service: WebhookService = Depends(),
):
    """Handle incoming Google Webhook notifications"""
    return webhook_service.notification_handler(request)
