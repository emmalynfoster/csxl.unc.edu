"""
The Academic Advising service allows the API to manipulate advising data in the database.
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


class AcademicAdvisingService:
    """Service that performs all of the actions on the `academic_advising` table."""

    def __init__(self, session: Session = Depends(db_session)):
        """Initializes the session."""
        self._session = session

    # Possible entity handler that takes in status of webhook and automatically handles create/update/delete by testing it against the database
    def handle_entity(self, entity_data: dict):
        """Handles creation, update, or deletion of an entity based on its status."""
        entity_id = entity_data.get("id")
        confirmed = entity_data.get(
            "confirmed"
        )  # Temp value, should be whatever response from the webhook/google api

        if confirmed:
            # Check if the entity exists in the database
            existing_entity = self._session.get(
                document_entity.DocumentEntity, entity_id
            )

            if existing_entity:
                # Update the existing entity
                existing_entity.title = entity_data.get("title", existing_entity.title)
                existing_entity.description = entity_data.get(
                    "description", existing_entity.description
                )
                existing_entity.last_modified_by = entity_data.get(
                    "last_modified_by", existing_entity.last_modified_by
                )
                existing_entity.modification_date = datetime.now()

                # Handle sections update
                if "sections" in entity_data:
                    existing_entity.sections.clear()
                    for section_data in entity_data["sections"]:
                        section_entity = (
                            document_section_entity.DocumentSectionEntity.from_model(
                                document_section.DocumentSection(**section_data)
                            )
                        )
                        existing_entity.sections.append(section_entity)

                self._session.commit()
                return "updated"
            else:
                # Create a new entity
                self.create_document(entity_data)
                return "created"
        else:
            # If not confirmed, check if the entity exists and delete it
            if self._session.get(document_entity.DocumentEntity, entity_id):
                self.delete_document(entity_id)
                return "deleted"

        raise ValueError("Invalid entity data or status.")

    def create_document(self, entity_data: dict) -> document.Document:
        """Create a new document with optional sections."""
        sections_data = entity_data.pop("sections", [])
        new_document = document_entity.DocumentEntity.from_model(
            document.Document(**entity_data)
        )

        # Create associated document sections if provided
        for section_data in sections_data:
            section_entity = document_section_entity.DocumentSectionEntity.from_model(
                document_section.DocumentSection(**section_data)
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
