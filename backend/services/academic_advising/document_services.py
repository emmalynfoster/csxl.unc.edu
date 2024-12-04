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

__authors__ = ["Nathan Kelete", "Emmalyn Foster"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class DocumentService:
    """Service to drop all existing documents and repopulate with new ones."""

    def __init__(self, session: Session = Depends(db_session)):
        """Initializes the session."""
        self._session = session

    # update when API responses are correctly parsed
    def refresh_documents(self) -> list[DocumentDetails]:
        """
        Drops all existing documents and repopulates the database with new data.

        Args:
            new_data (list[dict]): List of new document data.

        Returns:
            list[document.Document]: List of repopulated documents.
        """
        self.drop_all_documents()
        ## new data will come from API call (markdown_extraction.py)
        new_data=""
        return self.repopulate_documents(new_data)
    

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


    def create_document(self, entity_data: dict) -> DocumentDetails:
        """Create a new document with corresponding sections
        
            Args: entity_data: A dictionary of parsed data from the API response, each representing an individual document

            Returns:  Pydantic representation of Document
        """
        sections_data = entity_data["sections"]
        new_document = DocumentEntity(title=entity_data["title"], link=entity_data["link"])

        self._session.add(new_document)
        self._session.flush()  # Flush ensures `new_document.id` is available

        # Create associated document sections
        for section_data in sections_data:
            section_entity = DocumentSectionEntity(
                    title=section_data["title"],
                    content=section_data["content"],
                    document_id=new_document.id,
                )
            self._session.add(section_entity)
            self._session.flush() 
            new_document.doc_sections.append(section_entity)

        self._session.add(new_document)
        self._session.commit()
        return new_document.to_details_model()

    def get_document_by_id(self, id: int) -> DocumentDetails:
        """Retrieve a document by its ID, including its sections.
        
            Args: id of the document

            Returns: DocumentDetails: pydantic representation of queried Document
        """
        document_query = select(DocumentEntity).where(DocumentEntity.id == id)
        existing_document = self._session.scalars(document_query).one_or_none()

        if not existing_document:
            raise ResourceNotFoundException(f"No document found with matching ID: {id}")

        return existing_document.to_details_model()
    
    def get_document_sections(self, document: DocumentEntity) -> list[DocumentSection]:
        """Retrieve all of the sections attached to a document
        
            Args:
                document (DocumentEntity): The document entity whose sections are to be retrieved.

            Returns:
                list[DocumentSection]: A list of DocumentSection models corresponding to the sections.
        """

        # Query the sections directly via the relationship
        sections = self._session.query(DocumentSectionEntity).filter_by(document_id=document.id).all()
    
        # Convert entities to models before returning
        return [section.to_model() for section in sections]
    
    def all(self) -> list[DocumentDetails]:
        """Gets all documents from the database"""
        query = select(DocumentEntity).order_by(DocumentEntity.id)
        entities = self._session.scalars(query).all()

        # Convert entries to a model and return
        return [entity.to_details_model() for entity in entities]


