"""
The Document service allows the API to manipulate advising data in the database.
"""

from fastapi import Depends, HTTPException
from sqlalchemy import select, func, delete, text
from sqlalchemy.orm import Session
from datetime import datetime

from ...database import db_session
from ..exceptions import ResourceNotFoundException

from ...entities.academic_advising import DocumentEntity, DocumentSectionEntity
from ...models.academic_advising import DocumentDetails, DocumentSection
from ...models.academic_advising.document import Document

__authors__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class DocumentService:
    """Service to drop all existing documents and repopulate with new ones."""

    def __init__(self, session: Session = Depends(db_session)):
        """Initializes the session."""
        self._session = session

    def drop_all_documents(self) -> None:
        """Drop and recreate documents table to be repopulated"""
        self._session.execute(text("DROP TABLE IF EXISTS drop_in CASCADE"))
        self._session.commit()  # Commit the DROP TABLE to finalize it

        # Recreate the table using SQLAlchemy
        DocumentEntity.__table__.create(self._session.get_bind(), checkfirst=True)
        self._session.commit()

    def repopulate_documents(self, documents_data: list[dict]) -> list[DocumentDetails]:
        """
        Repopulates the document table with new data.

        Args:
            documents_data (list[dict]): A list of dictionaries, each representing a document.

        Returns:
            list[document.DocumentDetails]: List of inserted documents.
        """

        # Repopulate with new data
        repopulated_documents = []
        for data in documents_data:
            new_document = self.create_document(data)
            repopulated_documents.append(new_document)

        # Commit the new data to the database
        self._session.commit()

        return repopulated_documents

    def refresh_documents(self, new_data: list[dict]) -> list[DocumentDetails]:
        """
        Drops all existing documents and repopulates the database with new data.

        Args:
            new_data (list[dict]): List of new document data.

        Returns:
            list[document.Document]: List of repopulated documents.
        """
        self.drop_all_documents()
        return self.repopulate_documents(new_data)

    def create_document(self, entity_data: dict) -> DocumentDetails:
        """Create a new document with optional sections."""
        sections_data = entity_data["sections"]
        new_document = DocumentEntity.from_model(
            Document(id=entity_data["id"], title=entity_data["title"])
        )

        self._session.add(new_document)
        self._session.flush()  # Flush ensures `new_document.id` is available

        # Create associated document sections
        for section_data in sections_data:
            section_entity = DocumentSectionEntity.from_model(
                DocumentSection(
                    id=section_data["id"],
                    title=section_data["title"],
                    content=section_data["content"],
                    document_id=new_document.id,
                )
            )
            new_document.doc_sections.append(section_entity)

        for section in new_document.doc_sections:
            print(f"Section ID: {section.id} | TSV Content: {section.tsv_content}")

        self._session.add(new_document)
        return new_document.to_details_model()

    def get_document_by_id(self, entity_id: int) -> DocumentDetails:
        """Retrieve a document by its ID, including its sections."""
        document_query = select(DocumentEntity).where(DocumentEntity.id == entity_id)
        existing_document = self._session.scalars(document_query).one_or_none()

        if not existing_document:
            raise HTTPException(
                status_code=404, detail=f"Document with ID {entity_id} not found."
            )

        return existing_document.to_details_model()
