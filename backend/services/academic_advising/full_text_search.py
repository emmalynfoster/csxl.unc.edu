from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.entities.academic_advising.document_section_entity import (
    DocumentSectionEntity,
)


def search_document_sections(
    session: Session, search_query: str
) -> list[DocumentSectionEntity]:
    """
    Perform a full-text search on the DocumentSectionEntity and return ranked results.

    Args:
        session (Session): SQLAlchemy session object.
        search_query (str): The search query string.

    Returns:
        List[DocumentSectionEntity]: A list of DocumentSectionEntity objects ordered by relevance.
    """
    # Create a tsquery from the search string
    ts_query = func.to_tsquery("english", search_query)

    # Perform the search, rank the results, and return only the entities
    results = (
        session.query(DocumentSectionEntity)
        .filter(DocumentSectionEntity.tsv_content.op("@@")(ts_query))
        .order_by(func.ts_rank_cd(DocumentSectionEntity.tsv_content, ts_query).desc())
        .all()
    )

    return results
