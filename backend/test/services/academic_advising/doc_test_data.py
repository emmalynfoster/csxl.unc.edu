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
    "confirmed": True,  # Flag to indicate if the webhook confirmed the data
    "sections": [
        {
            "id": 101,
            "title": "Introduction",
            "content": "Overview of the advising process.",
        },
        {
            "id": 102,
            "title": "CS Department Policies",
            "content": "Details on advising specific to the Computer Science department.",
        },
    ],
}

DOC_DATA_2 = {
    "id": 2,
    "title": "New Advising Document",
    "description": "Details about new advising policies.",
    "created_by": "staff",
    "last_modified_by": "staff",
    "confirmed": True,
    "sections": [
        {
            "id": 103,
            "title": "General Policies",
            "content": "Explanation of general advising policies.",
        },
        {
            "id": 104,
            "title": "Special Cases",
            "content": "Advising information for unique circumstances.",
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
            title=document["title"]
        )

        for section in document["sections"]:
            new_section = DocumentSectionEntity(
                id=section["id"],
                title=section["title"],
                content=section["content"],
                document_id=new_document["id"],
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