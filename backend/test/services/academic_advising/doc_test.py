"""Tests for the Document Services."""

from unittest.mock import create_autospec
import pytest
from backend.services.exceptions import (
    ResourceNotFoundException,
    UserPermissionException,
)

from backend.models.academic_advising import DocumentDetails, DocumentSection
from backend.services.academic_advising.document_services import DocumentService

from .doc_test_data import (
    ENTITY_DATA_CREATE,
    ENTITY_DATA_BASE,
    ENTITY_DATA_DELETE,
    ENTITY_DATA_UPDATE,
    fake_data_fixture,
)
from . import doc_test_data


__authors__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


def test_create_document(document_svc: DocumentService):
    """Test creating a new document."""
    # Use ENTITY_DATA_CREATE as test input
    created_document = document_svc.create_document(ENTITY_DATA_CREATE)

    # Assert the document was created correctly
    assert created_document.title == ENTITY_DATA_CREATE["title"]
    assert created_document.description == ENTITY_DATA_CREATE["description"]
    assert len(created_document.sections) == len(ENTITY_DATA_CREATE["sections"])


def test_get_document_by_id(document_svc: DocumentService):
    """Test retrieving a document by its ID."""
    # Fetch the base document
    document_id = ENTITY_DATA_BASE["id"]
    fetched_document = document_svc.get_document_by_id(document_id)

    # Assert the fetched document matches the base data
    assert fetched_document.id == document_id
    assert fetched_document.title == ENTITY_DATA_BASE["title"]
    assert len(fetched_document.sections) == len(ENTITY_DATA_BASE["sections"])


def test_update_document(document_svc: DocumentService):
    """Test updating an existing document."""

    # Use ENTITY_DATA_UPDATE as test input
    updated_document = document_svc.update_document(
        ENTITY_DATA_UPDATE["id"], ENTITY_DATA_UPDATE
    )

    # Assert the document was updated correctly
    assert updated_document.title == ENTITY_DATA_UPDATE["title"]
    assert len(updated_document.sections) == len(ENTITY_DATA_UPDATE["sections"])
    assert any(
        section["title"] == "Frequently Asked Questions"
        for section in ENTITY_DATA_UPDATE["sections"]
    )


def test_delete_document(document_svc: DocumentService):
    """Test deleting a document."""

    # Delete the document
    document_id = ENTITY_DATA_DELETE["id"]
    document_svc.delete_document(document_id)

    # Assert the document no longer exists
    with pytest.raises(ResourceNotFoundException):
        document_svc.get_document_by_id(document_id)


def test_get_nonexistent_document(document_svc: DocumentService):
    """Test retrieving a non-existent document."""

    # Assert that fetching a non-existent document raises an exception
    nonexistent_id = 9999
    with pytest.raises(ResourceNotFoundException):
        document_svc.get_document_by_id(nonexistent_id)
