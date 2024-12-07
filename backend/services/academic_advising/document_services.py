"""
The Document service allows the API to manipulate advising data in the database.
"""

import re
from fastapi import Depends, HTTPException
from sqlalchemy import select, func, delete, text
from sqlalchemy.orm import Session
from datetime import datetime
from ...env import getenv

from ...database import db_session
from ..exceptions import ResourceNotFoundException

from ...entities.academic_advising import DocumentEntity, DocumentSectionEntity
from ...models.academic_advising import DocumentDetails, DocumentSection
from ...models.academic_advising.document import Document
from .markdown_extraction import retrieve_documents

__authors__ = ["Nathan Kelete", "Emmalyn Foster"]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class DocumentService:
    """Service to drop all existing documents and repopulate with new ones."""

    def __init__(self, session: Session = Depends(db_session)):
        """Initializes the session."""
        self._session = session
        self.global_folder_id = getenv("GOOGLE_FOLDER_ID")

    def refresh_documents(self) -> list[DocumentDetails]:
        """
        Drops all existing documents and repopulates the database with new data.

        Returns:
            list[DocumentDetails]: List of repopulated documents.
        """
        self.drop_all_documents()
        # retrieve documents from markdown_extraction.py
        document_data = retrieve_documents(self.global_folder_id)
        return self.repopulate_documents(document_data)

    def drop_all_documents(self) -> None:
        """Drop and recreate documents table to be repopulated"""
        self._session.execute(delete(DocumentSectionEntity))
        self._session.execute(delete(DocumentEntity))
        self._session.commit()

        # Reset ID sequences
        self._session.execute(text("ALTER SEQUENCE section_id_seq RESTART WITH 1"))
        self._session.execute(text("ALTER SEQUENCE document_id_seq RESTART WITH 1"))
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
        new_document = DocumentEntity(
            title=entity_data["title"], link=entity_data["link"]
        )

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

        self._session.add(new_document)
        # here for testing, but should only commit after all entities are successfully created and added
        # self._session.commit()
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
    
    def get_section_by_id(self, id: int) -> DocumentSection:
        """Retrieve an document section by id
        
            Args: 
                id: an int representing the section id in the database

            Returns: 
                DocumentSectionEntity attached to the id
        """
        section = self._session.scalars(select(DocumentSectionEntity).where(DocumentSectionEntity.id == id)).one_or_none()
        
        if not section:
            raise ResourceNotFoundException(f"No document section found with matching ID: {id}")
        
        return section.to_model()

    def get_document_sections(self, document: DocumentEntity) -> list[DocumentSection]:
        """Retrieve all of the sections attached to a document

        Args:
            document (DocumentEntity): The document entity whose sections are to be retrieved.

        Returns:
            list[DocumentSection]: A list of DocumentSection models corresponding to the sections.
        """

        # Query the sections directly via the relationship
        sections = (
            self._session.query(DocumentSectionEntity)
            .filter_by(document_id=document.id)
            .all()
        )

        # Convert entities to models before returning
        return [section.to_model() for section in sections]

    def get_document_from_section(
        self, section: DocumentSection
    ) -> DocumentDetails:
        """Retrieve the document object attached to its section in order to group search results by document

        Args:
            document section (DocumentSectionEntity)

        Returns:
            DocumentDetails: The corresponding document with its sections
        """

        document = (
            self._session.query(DocumentEntity)
            .filter_by(id=section.document_id)
            .one_or_none()
        )
        
        return document

    def all(self) -> list[DocumentDetails]:
        """Gets all documents from the database"""
        query = select(DocumentEntity).order_by(DocumentEntity.id)
        entities = self._session.scalars(query).all()

        # Convert entries to a model and return
        return [entity.to_details_model() for entity in entities]

    def handle_query(self, query: str) -> str:
        """Reformats search queries to avoid errors for document full-text search"""
        # Define characters that need to be escaped in tsquery
        special_chars = r"&|!():"
        # Escape special characters
        escaped_query = re.sub(rf"([{re.escape(special_chars)}])", r"\\\1", query)
        # Replace spaces with ' & ' for logical AND
        return escaped_query.replace(" ", " & ")

    def search_document_sections(self, search_query: str) -> list[DocumentSection]:
        """
        Perform a full-text search on the DocumentSectionEntity and return ranked results.

        Args:
            session (Session): SQLAlchemy session object.
            search_query (str): The search query string.

        Returns:
            List[DocumentSectionEntity]: A list of DocumentSectionEntity objects ordered by relevance.
        """
        formatted_search_query = self.handle_query(search_query)

        # Create a tsquery from the search string
        ts_query = func.to_tsquery("english", formatted_search_query)

        # Perform the search, rank the results, and return only the entities
        results = (
            self._session.query(DocumentSectionEntity)
            .filter(DocumentSectionEntity.tsv_content.op("@@")(ts_query))
            .order_by(
                func.ts_rank_cd(DocumentSectionEntity.tsv_content, ts_query).desc()
            )
            .all()
        )

        return [result.to_model() for result in results]
