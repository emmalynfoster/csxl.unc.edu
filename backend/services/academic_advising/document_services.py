"""
The Document service allows the API to manipulate advising data in the database.
"""

from fastapi import Depends, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session
from datetime import datetime

from ...database import db_session
from ..exceptions import ResourceNotFoundException

from ...entities.academic_advising import document_entity, document_section_entity

from ...models.academic_advising import document, document_details, document_section

__authors__ = ["Nathan Kelete"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"

class DocumentService:
    """Service to drop all existing documents and repopulate with new ones."""

    def __init__(self, session: Session = Depends(db_session)):
        """Initializes the session."""
        self._session = session

    def drop_all_documents(self) -> None:
        """Delete all existing documents and their sections."""
        self._session.execute(delete(document_section_entity.DocumentSectionEntity))
        self._session.execute(delete(document_entity.DocumentEntity))
        self._session.commit()

    def repopulate_documents(
        self, documents_data: list[dict]
    ) -> list[document.Document]:
        """
        Repopulates the document table with new data.

        Args:
            documents_data (list[dict]): A list of dictionaries, each representing a document.

        Returns:
            list[document.Document]: List of inserted documents.
        """
        # Clear the existing table data
        self._session.query(document_entity.DocumentEntity).delete()
        self._session.commit()

        # Repopulate with new data
        repopulated_documents = []
        for data in documents_data:
            # Extract document metadata and sections
            sections_data = data.pop("sections", [])
            new_document = document_entity.DocumentEntity.from_model(
                document.Document(
                    id=data["id"], title=data["title"], doc_sections=sections_data
                )
            )

            # Add sections
            for section in sections_data:
                section_entity = (
                    document_section_entity.DocumentSectionEntity.from_model(
                        document_section.DocumentSection(
                            id=section["id"],
                            title=section["title"],
                            content=section["content"],
                        )
                    )
                )
                new_document.sections.append(section_entity)

            # Add the new document to the session
            self._session.add(new_document)
            repopulated_documents.append(new_document.to_details_model())

        # Commit the new data to the database
        self._session.commit()

        return repopulated_documents

    def refresh_documents(self, new_data: list[dict]) -> list[document.Document]:
        """
        Drops all existing documents and repopulates the database with new data.

        Args:
            new_data (list[dict]): List of new document data.

        Returns:
            list[document.Document]: List of repopulated documents.
        """
        self.drop_all_documents()
        return self.repopulate_documents(new_data)

    def create_document(self, entity_data: dict) -> document.Document:
        """Create a new document with optional sections."""
        sections_data = entity_data.pop("sections", [])
        new_document = document_entity.DocumentEntity.from_model(
            document.Document(id=entity_data["id"], title=entity_data["title"])
        )

        # Create associated document sections
        for section_data in sections_data:
            section_entity = document_section_entity.DocumentSectionEntity.from_model(
                document_section.DocumentSection(
                    id=section_data["id"],
                    title=section_data["title"],
                    content=section_data["content"],
                )
            )
            new_document.sections.append(section_entity)

        self._session.add(new_document)
        self._session.commit()
        return new_document.to_details_model()

    def update_document(
        self, entity_id: int, updated_data: document.Document
    ) -> document_details.DocumentDetails:
        """Updates an existing document and its sections.

        Args:
            entity_id (int): The ID of the document to update.
            updated_data (document.Document): The updated document data.

        Returns:
            DocumentDetails: The updated document model.

        Raises:
            ResourceNotFoundException: If the document is not found.
        """
        # Query the document with matching ID
        obj = self._session.get(document_entity.DocumentEntity, entity_id)

        # Throw ResourceNotFoundException if the document doesn't exist
        if obj is None:
            raise ResourceNotFoundException(
                f"Document does not exist for id {entity_id}"
            )

        # Update document fields explicitly
        obj.title = updated_data.title
        obj.description = updated_data.description
        obj.created_by = updated_data.created_by
        obj.last_modified_by = updated_data.last_modified_by
        obj.creation_date = updated_data.creation_date
        obj.modification_date = updated_data.modification_date

        # Handle sections if provided
        if updated_data.sections is not None:
            # Clear existing sections
            obj.sections.clear()
            # Add updated sections
            for section_data in updated_data.sections:
                section_entity = (
                    document_section_entity.DocumentSectionEntity.from_model(
                        section_data
                    )
                )
                obj.sections.append(section_entity)

        # Save changes
        self._session.commit()

        # Return updated document details
        return obj.to_details_model()

    def delete_document(self, entity_id: int) -> None:
        """Delete a document and its sections."""
        delete_query = delete(document_entity.DocumentEntity).where(
            document_entity.DocumentEntity.id == entity_id
        )
        result = self._session.execute(delete_query)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=404, detail=f"Document with ID {entity_id} not found."
            )
        self._session.commit()

    def get_document_by_id(self, entity_id: int) -> document.Document:
        """Retrieve a document by its ID, including its sections."""
        document_query = select(document_entity.DocumentEntity).where(
            document_entity.DocumentEntity.id == entity_id
        )
        existing_document = self._session.scalars(document_query).one_or_none()

        if not existing_document:
            raise HTTPException(
                status_code=404, detail=f"Document with ID {entity_id} not found."
            )

        return existing_document.to_details_model()
