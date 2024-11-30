import pytest
from sqlalchemy.orm import Session
from ....models.academic_advising import DocumentDetails, DocumentSection
from ....entities.academic_advising import DocumentEntity, DocumentSectionEntity
from ..reset_table_id_seq import reset_table_id_seq

# Sample data objects
ENTITY_DATA_BASE = {
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

ENTITY_DATA_CREATE = {
    "title": "New Advising Document",
    "description": "Details about new advising policies.",
    "created_by": "staff",
    "last_modified_by": "staff",
    "confirmed": True,
    "sections": [
        {
            "title": "General Policies",
            "content": "Explanation of general advising policies.",
        },
        {
            "title": "Special Cases",
            "content": "Advising information for unique circumstances.",
        },
    ],
}

ENTITY_DATA_UPDATE = {
    "id": 1,
    "title": "Updated Advising Guidelines",
    "description": "Revised comprehensive guidelines for academic advising.",
    "last_modified_by": "advisor",
    "confirmed": True,
    "sections": [
        {
            "id": 101,
            "title": "Introduction Updated",
            "content": "Updated overview of the advising process.",
        },
        {
            "id": 103,  # Adding a new section
            "title": "Frequently Asked Questions",
            "content": "Answers to common advising questions.",
        },
    ],
}

ENTITY_DATA_DELETE = {
    "id": 1,
    "confirmed": False,  # Indicates the entity should be deleted
}

documents = [
    ENTITY_DATA_BASE,
    ENTITY_DATA_CREATE,
    ENTITY_DATA_UPDATE,
    ENTITY_DATA_DELETE,
]


def insert_fake_data(session: Session):
    """Inserts fake data into the database for testing."""

    # Step 1: Insert the base document with its sections
    base_document = DocumentEntity(
        id=ENTITY_DATA_BASE["id"],
        title=ENTITY_DATA_BASE["title"],
        confirmed=ENTITY_DATA_BASE["confirmed"],
    )

    for section in ENTITY_DATA_BASE["sections"]:
        base_section = DocumentSectionEntity(
            id=section["id"],
            title=section["title"],
            content=section["content"],
            document_id=ENTITY_DATA_BASE["id"],
        )
        base_document.sections.append(base_section)

    session.add(base_document)

    # Step 2: Add the create test document
    create_document = DocumentEntity(
        title=ENTITY_DATA_CREATE["title"],
        description=ENTITY_DATA_CREATE["description"],
        created_by=ENTITY_DATA_CREATE["created_by"],
        last_modified_by=ENTITY_DATA_CREATE["last_modified_by"],
        confirmed=ENTITY_DATA_CREATE["confirmed"],
    )

    for section in ENTITY_DATA_CREATE["sections"]:
        create_section = DocumentSectionEntity(
            title=section["title"],
            content=section["content"],
        )
        create_document.sections.append(create_section)

    session.add(create_document)

    # Step 4: Reset sequence IDs for consistent test behavior
    reset_table_id_seq(
        session,
        DocumentEntity,
        DocumentEntity.id,
        ENTITY_DATA_BASE["id"] + len(documents),
    )
    reset_table_id_seq(
        session,
        DocumentSectionEntity,
        DocumentSectionEntity.id,
        sum(len(doc["sections"]) for doc in [ENTITY_DATA_BASE, ENTITY_DATA_CREATE]) + 1,
    )

    # Commit all changes to the database
    session.commit()


@pytest.fixture(autouse=True)
def fake_data_fixture(session: Session):
    insert_fake_data(session)
    session.commit()
    yield
