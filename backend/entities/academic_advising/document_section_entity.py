from sqlalchemy import Integer, String, ForeignKey, Index, text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, mapper


from ..entity_base import EntityBase
from typing import Self
from sqlalchemy.dialects.postgresql import TSVECTOR
from ...models.academic_advising.document_section import DocumentSection

__authors__ = ["Nathan Kelete", Emmalyn Foster]
__copyright__ = "Copyright 2024"
__license__ = "MIT"


class DocumentSectionEntity(EntityBase):
    """Serves as the database model schema defining the shape of the `DocumentSection" table"""

    # Name for the DocumentSection table in the PostgreSQL database
    __tablename__ = "section"

    # DocumentSection properties (columns in the database table)

    # Unique ID for the DocumentSection
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Title of the document section
    title: Mapped[str] = mapped_column(String, nullable=False)

    # Content of the document section
    content: Mapped[str] = mapped_column(String, nullable=False)

    # Full-text search vector for the document section
    tsv_content: Mapped[str] = mapped_column(TSVECTOR, nullable=False)

    # NOTE: This defines a one-to-many relationship between the document and section tables.
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"))
    document: Mapped["DocumentEntity"] = relationship(back_populates="doc_sections")

    # Index for the full-text search vector
    __table_args__ = (
        Index("ix_document_section_content_tsv", tsv_content, postgresql_using="gin"),
    )

    @classmethod
    def from_model(cls, model: DocumentSection) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            content=model.content,
            document_id=model.document_id,
        )

    def to_model(self) -> DocumentSection:
        return DocumentSection(
            id=self.id,
            title=self.title,
            content=self.content,
            document_id=self.document_id,
        )


# Automatically populate the `tsv_content` column
@event.listens_for(DocumentSectionEntity, "before_insert")
@event.listens_for(DocumentSectionEntity, "before_update")
def update_tsv_content(mapper, connection, target):  # type: ignore
    tsvector_value = connection.execute(
        text("SELECT to_tsvector(:content || ' ' || :title)"),
        {"content": target.content, "title": target.title},
    ).scalar()
    target.tsv_content = tsvector_value
