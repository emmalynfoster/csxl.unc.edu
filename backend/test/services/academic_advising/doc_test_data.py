"""Contains mock data for demo and testing DocumentService"""

import pytest
from sqlalchemy.orm import Session
from ....models.academic_advising import DocumentDetails, DocumentSection
from ....entities.academic_advising import DocumentEntity, DocumentSectionEntity
from ..reset_table_id_seq import reset_table_id_seq

# Sample data from API response, inserted as a document entry into DB
# It is necessary to use response data instead of creating DocumentSectionEntities directly b/c of tsv_content population

DOC_DATA_1 = {
    "id": 1,  # Unique ID for the document
    "title": "Advising Guidelines",
    "link": "link",
    "sections": [
        {
            "title": "Introduction",
            "content": "Overview of the advising process.",
        },
        {
            "title": "CS Department Policies",
            "content": "Details on advising specific to the Computer Science department.",
        },
    ],
}

DOC_DATA_2 = {
    "id": 2,
    "title": "Advising Document",
    "link": "link",
    "sections": [
        {
            "title": "General Policies",
            "content": "Explanation of general advising policies.",
        },
        {
            "title": "Special Cases",
            "content": "Advising information for unique circumstances.",
        },
    ]
}

DOC_TO_CREATE = {
    "title": "New Advising Document",
    "link": "link",
    "sections": [
        {
            "title": "Register for COMP 210",
            "content": "How to register for COMP 210",
        },
        {
            "title": "Register for COMP 590",
            "content": "How to register for COMP 590",
        },
    ]
}


documents = [
    DOC_DATA_1,
    DOC_DATA_2
]


def insert_fake_data(session: Session):
    """Inserts fake data into the database for testing."""

    # Step 1: Insert the base document with its sections
    for document in documents:
        new_document = DocumentEntity(
            id=document["id"],
            title=document["title"],
            link=document["link"]
        )

        for section in document["sections"]:
            new_section = DocumentSectionEntity(
                title=section["title"],
                content=section["content"],
                document_id=document["id"],
            )
            new_document.doc_sections.append(new_section)

        session.add(new_document)

    # Step 4: Reset sequence IDs for consistent test behavior
    reset_table_id_seq(
        session,
        DocumentEntity,
        DocumentEntity.id,
        DOC_DATA_1["id"] + len(documents),
    )

    reset_table_id_seq(
        session,
        DocumentSectionEntity,
        DocumentSectionEntity.id,
        sum(len(doc["sections"]) for doc in [DOC_DATA_1]) + 1,
    )

    # Commit all changes to the database
    session.commit()


@pytest.fixture(autouse=True)
def fake_data_fixture(session: Session):
    insert_fake_data(session)
    session.commit()
    yield