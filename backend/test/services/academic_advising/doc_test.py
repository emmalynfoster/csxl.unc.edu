"""Tests for the Document Services."""

import subprocess
from unittest.mock import create_autospec
import pytest
from backend.services.exceptions import (
    ResourceNotFoundException,
    UserPermissionException,
)

from ..fixtures import document_svc
from backend.models.academic_advising import DocumentDetails, DocumentSection
from backend.services.academic_advising.document_services import DocumentService

from .doc_test_data import (
    DOC_DATA_1,
    DOC_DATA_2,
    DOC_TO_CREATE,
    fake_data_fixture,
)
from . import doc_test_data


__authors__ = ["Nathan Kelete", "Emmalyn Foster"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


def test_create_document(document_svc: DocumentService):
    """Test creating a new document."""

    created_document = document_svc.create_document(DOC_TO_CREATE)
    from_db = document_svc.get_document_by_id(created_document.id)
    # Assert the document was created correctly
    assert created_document.id is not None
    assert created_document.title == DOC_TO_CREATE["title"]
    assert len(created_document.sections) == len(DOC_TO_CREATE["sections"])
    assert from_db is not None
    assert from_db.id is not None
    assert from_db.title == created_document.title
    assert len(from_db.sections) == len(created_document.sections)


def test_get_document_by_id(document_svc: DocumentService):
    """Test retrieving a document by its ID."""
    document_id = DOC_DATA_1["id"]
    fetched_document = document_svc.get_document_by_id(document_id)

    assert fetched_document.id == document_id
    assert fetched_document.title == DOC_DATA_1["title"]
    assert len(fetched_document.sections) == len(DOC_DATA_2["sections"])


def test_all(document_svc: DocumentService):
    """Test getting all documents"""
    documents = document_svc.all()
    assert documents is not None
    assert len(documents) == len(doc_test_data.documents)


def test_get_nonexistent_document(document_svc: DocumentService):
    """Test retrieving a non-existent document."""
    # Assert that fetching a non-existent document raises an exception
    nonexistent_id = 9999
    with pytest.raises(ResourceNotFoundException):
        document_svc.get_document_by_id(nonexistent_id)
        pytest.fail()


def test_get_document_sections(document_svc: DocumentService):
    """Test getting the sections associated with a document"""
    document = document_svc.get_document_by_id(DOC_DATA_1["id"])
    doc_sections = document_svc.get_document_sections(document)

    assert len(doc_sections) == len(document.sections)
    assert doc_sections[0].title == document.sections[0].title
    assert doc_sections[0].id == document.sections[0].id


def test_refresh_documents(document_svc: DocumentService):
    """Tests dropping the Document table and repopulating it on webhook notification to receive all updates"""
    inserted_documents = document_svc.refresh_documents()

    assert inserted_documents is not None
    assert len(document_svc.all()) > 0

    # Important to prevent conflicts when testing other services
    subprocess.run(
        [
            "python3",
            "-m",
            "backend.script.reset_demo",
        ],  # Command to reset the database to test data
        capture_output=True,  # Capture output to check for errors
        text=True,  # Capture output as text
    )


def test_search_documents(document_svc: DocumentService):
    """Test search queries on documents"""
    results = document_svc.search_document_sections("Introduction")
    assert len(results) == 1


def test_search_documents_general(document_svc: DocumentService):
    """Test search queries on documents"""
    results = document_svc.search_document_sections("advising")
    assert len(results) > 1
