from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, func, Index, text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, mapper


from ..entity_base import EntityBase
from typing import Self
from sqlalchemy.dialects.postgresql import TSVECTOR
from ...models.academic_advising.document_section import DocumentSection
from ...models.academic_advising.document_details import DocumentDetails


class DocumentSectionEntity(EntityBase):
    __tablename__ = "section"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    tsv_content: Mapped[str] = mapped_column(TSVECTOR, nullable=False)


    # NOTE: This defines a one-to-many relationship between the document and section tables.
    document_id: Mapped[int] = mapped_column(ForeignKey("document.id"))
    document: Mapped["DocumentEntity"] = relationship(back_populates="doc_sections")

    __table_args__ = (
        Index(
            "ix_document_section_content_tsv",
            tsv_content,
            postgresql_using="gin"
        ),
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
def update_tsv_content(mapper, connection, target): # type: ignore
    target.tsv_content = connection.execute(
        func.to_tsvector(target.content)
    ).scalar()