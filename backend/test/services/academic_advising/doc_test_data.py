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
    "link": "https://docs.google.com",
    "sections": [
        {
            "id":1,
            "title": "# Introduction",
            "content": "Overview of the advising process.",
        },
        {
            "id":2,
            "title": "# CS Department Policies",
            "content": "Details on advising specific to the Computer Science department.",
        },
    ],
}

DOC_DATA_2 = {
    "id": 2,
    "title": "Advising Document",
    "link": "https://docs.google.com",
    "sections": [
        {
            "id":3,
            "title": "# General Policies",
            "content": "Explanation of general advising policies.",
        },
        {
            "id":4,
            "title": "# Special Cases",
            "content": "Advising information for unique circumstances.",
        },
    ],
}

DOC_DATA_WITH_TABLE = {
    "id": 3,
    "title": "Register for COMP 590",
    "link": "https://docs.google.com",
    "sections": [
        {
            "id":5,
            "title": "## Registering for (or dropping) COMP 590",
            "content": 'All COMP 590 sections require COMP 211 and COMP 301 as prerequisites (unless noted below). Each COMP 590 section may have different registration procedures and/or additional expected prerequisites. Please refer to the table below. \n\nFor sections that are marked as "instructor consent required", please contact the instructor to obtain approval (a simple email exchange will suffice) and then submit a [Manual Registration Request](https://forms.gle/opaRMyC9q2nw4fXL8). Please see bottom of this page for important instructions with regard to manual registration requests. \n\nWARNING: dropping a COMP 590 in ConnectCarolina will drop ALL COMP 590\'s from your schedule. So if you need to drop a COMP 590 and you are registered for more than one, please contact our undergraduate student services manager Brandon Byrd (bbyrd@cs.unc.edu) and he should be able to help you.\n\n| Section | Topic | Instructor | Registration / Background |\n| :---- | :---- | :---- | :---- |\n| 059 | [Programming Methods, Models, Languages, and Analysis](https://www.cs.unc.edu/~stotts/COMP590-059-f24/blurb.txt) | David Stotts | Self-Registration |\n| 132 | [Formal Methods For System Security](https://www.cs.unc.edu/~csturton/courses/verifiedsec/) | Cynthia Sturton | Self-Registration |\n| 140 | Foundations of Software Engineering | Kris Jordan | Self-Registration |\n| 159 | Interactive Computer Graphics using WebGL and HTML5 | Brent Munsell | Self-Registration |\n| 175 | Computational Imaging | Praneeth Chakravarthula | Self-Registration |',
        },
    ],
}

DOC_TO_CREATE = {
    "title": "New Advising Document",
    "link": "https://docs.google.com",
    "sections": [
        {
            "title": "# Register for COMP 210",
            "content": "How to register for COMP 210",
        },
        {
            "title": "# Register for COMP 590",
            "content": "How to register for COMP 590",
        },
    ],
}


documents = [DOC_DATA_1, DOC_DATA_2, DOC_DATA_WITH_TABLE]


def insert_fake_data(session: Session):
    """Inserts fake data into the database for testing."""

    # Step 1: Insert the base document with its sections
    for document in documents:
        new_document = DocumentEntity(
            id=document["id"], title=document["title"], link=document["link"]
        )

        for section in document["sections"]:
            new_section = DocumentSectionEntity(
                id=section["id"],
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
        sum(len(doc["sections"]) for doc in documents) + 1,
    )

    # Commit all changes to the database
    session.commit()


@pytest.fixture(autouse=True)
def fake_data_fixture(session: Session):
    insert_fake_data(session)
    session.commit()
    yield
